/* my_chown.c - A hybrid implementation of chown with chmod functionality
 * This program changes the ownership and permissions of files and directories
 * Usage: my_chown [OPTION]... [OWNER][:[GROUP]] [MODE] FILE...
 */

#define _GNU_SOURCE
#define _DEFAULT_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <pwd.h>
#include <grp.h>
#include <errno.h>
#include <getopt.h>
#include <dirent.h>
#include <ctype.h>

/* Program options */
struct options {
    int recursive;      /* -R flag */
    int verbose;        /* -v flag */
    int changes_only;   /* -c flag */
    int quiet;          /* -f flag */
    int dereference;    /* -L flag (follow symlinks) */
    int no_dereference; /* -h flag (don't follow symlinks) */
    int change_perms;   /* whether to change permissions */
};

/* Function prototypes */
static void usage(void);
static int parse_owner_group(const char *spec, uid_t *uid, gid_t *gid);
static int parse_mode(const char *mode_str, mode_t *mode, int is_symbolic);
static int is_numeric_mode(const char *str);
static mode_t parse_numeric_mode(const char *str);
static mode_t parse_symbolic_mode(const char *str, mode_t current_mode);
static int change_ownership_and_perms(const char *path, uid_t uid, gid_t gid, mode_t mode, struct options *opts);
static int change_ownership_and_perms_recursive(const char *path, uid_t uid, gid_t gid, mode_t mode, struct options *opts);
static void print_change(const char *path, uid_t old_uid, gid_t old_gid, uid_t new_uid, gid_t new_gid, mode_t old_mode, mode_t new_mode, struct options *opts);
static const char *mode_to_string(mode_t mode);

static void usage(void) {
    printf("Usage: my_chown [OPTION]... [OWNER][:[GROUP]] [MODE] FILE...\n");
    printf("Change the owner, group, and/or permissions of each FILE.\n\n");
    printf("Options:\n");
    printf("  -c, --changes          like verbose but report only when a change is made\n");
    printf("  -f, --silent, --quiet  suppress most error messages\n");
    printf("  -v, --verbose          output a diagnostic for every file processed\n");
    printf("  -R, --recursive        operate on files and directories recursively\n");
    printf("  -h, --no-dereference   affect symbolic links instead of any referenced file\n");
    printf("  -L, --dereference      dereference all symbolic links\n");
    printf("      --help             display this help and exit\n");
    printf("      --version          output version information and exit\n\n");
    printf("MODE can be:\n");
    printf("  - Numeric (octal): 755, 644, etc.\n");
    printf("  - Symbolic: u+x, g-w, o=r, a+rw, etc.\n\n");
    printf("Examples:\n");
    printf("  my_chown root /u              Change the owner of /u to \"root\".\n");
    printf("  my_chown root:staff /u        Change owner to \"root\" and group to \"staff\".\n");
    printf("  my_chown root 755 /u          Change owner to \"root\" and permissions to 755.\n");
    printf("  my_chown root:staff 644 /u    Change owner, group, and permissions.\n");
    printf("  my_chown :staff u+x /u        Change group and add execute for user.\n");
    printf("  my_chown -hR root 755 /u      Recursively change owner and permissions.\n");
}

/* Parse owner:group specification */
static int parse_owner_group(const char *spec, uid_t *uid, gid_t *gid) {
    char *spec_copy = strdup(spec);
    char *colon_pos = strchr(spec_copy, ':');
    struct passwd *pwd;
    struct group *grp;
    
    *uid = (uid_t)-1;  /* -1 means don't change */
    *gid = (gid_t)-1;  /* -1 means don't change */
    
    if (colon_pos) {
        *colon_pos = '\0';
        
        /* Parse owner part */
        if (strlen(spec_copy) > 0) {
            pwd = getpwnam(spec_copy);
            if (pwd) {
                *uid = pwd->pw_uid;
            } else {
                /* Try to parse as numeric UID */
                char *endptr;
                long uid_long = strtol(spec_copy, &endptr, 10);
                if (*endptr == '\0' && uid_long >= 0) {
                    *uid = (uid_t)uid_long;
                } else {
                    fprintf(stderr, "my_chown: invalid user: '%s'\n", spec_copy);
                    free(spec_copy);
                    return -1;
                }
            }
        }
        
        /* Parse group part */
        if (strlen(colon_pos + 1) > 0) {
            grp = getgrnam(colon_pos + 1);
            if (grp) {
                *gid = grp->gr_gid;
            } else {
                /* Try to parse as numeric GID */
                char *endptr;
                long gid_long = strtol(colon_pos + 1, &endptr, 10);
                if (*endptr == '\0' && gid_long >= 0) {
                    *gid = (gid_t)gid_long;
                } else {
                    fprintf(stderr, "my_chown: invalid group: '%s'\n", colon_pos + 1);
                    free(spec_copy);
                    return -1;
                }
            }
        }
    } else {
        /* Only owner specified */
        pwd = getpwnam(spec_copy);
        if (pwd) {
            *uid = pwd->pw_uid;
        } else {
            /* Try to parse as numeric UID */
            char *endptr;
            long uid_long = strtol(spec_copy, &endptr, 10);
            if (*endptr == '\0' && uid_long >= 0) {
                *uid = (uid_t)uid_long;
            } else {
                fprintf(stderr, "my_chown: invalid user: '%s'\n", spec_copy);
                free(spec_copy);
                return -1;
            }
        }
    }
    
    free(spec_copy);
    return 0;
}

/* Check if a string represents a numeric mode */
static int is_numeric_mode(const char *str) {
    if (!str || strlen(str) == 0) return 0;
    
    for (size_t i = 0; i < strlen(str); i++) {
        if (!isdigit(str[i])) return 0;
    }
    return 1;
}

/* Parse numeric mode (e.g., "755", "644") */
static mode_t parse_numeric_mode(const char *str) {
    char *endptr;
    long mode_long = strtol(str, &endptr, 8);  /* Parse as octal */
    
    if (*endptr != '\0' || mode_long < 0 || mode_long > 07777) {
        return (mode_t)-1;  /* Invalid mode */
    }
    
    return (mode_t)mode_long;
}

/* Parse symbolic mode (e.g., "u+x", "g-w", "o=r") */
static mode_t parse_symbolic_mode(const char *str, mode_t current_mode) {
    mode_t new_mode = current_mode;
    char *mode_copy = strdup(str);
    char *token = strtok(mode_copy, ",");
    
    while (token) {
        char *ptr = token;
        mode_t who_mask = 0;
        char op = 0;
        mode_t perm_mask = 0;
        
        /* Parse who (u, g, o, a) */
        while (*ptr && strchr("ugoa", *ptr)) {
            switch (*ptr) {
                case 'u': who_mask |= S_IRWXU; break;
                case 'g': who_mask |= S_IRWXG; break;
                case 'o': who_mask |= S_IRWXO; break;
                case 'a': who_mask |= S_IRWXU | S_IRWXG | S_IRWXO; break;
            }
            ptr++;
        }
        
        /* If no who specified, default to 'a' */
        if (who_mask == 0) {
            who_mask = S_IRWXU | S_IRWXG | S_IRWXO;
        }
        
        /* Parse operator (+, -, =) */
        if (*ptr && strchr("+-=", *ptr)) {
            op = *ptr++;
        } else {
            free(mode_copy);
            return (mode_t)-1;  /* Invalid format */
        }
        
        /* Parse permissions (r, w, x) */
        while (*ptr && strchr("rwx", *ptr)) {
            switch (*ptr) {
                case 'r':
                    if (who_mask & S_IRWXU) perm_mask |= S_IRUSR;
                    if (who_mask & S_IRWXG) perm_mask |= S_IRGRP;
                    if (who_mask & S_IRWXO) perm_mask |= S_IROTH;
                    break;
                case 'w':
                    if (who_mask & S_IRWXU) perm_mask |= S_IWUSR;
                    if (who_mask & S_IRWXG) perm_mask |= S_IWGRP;
                    if (who_mask & S_IRWXO) perm_mask |= S_IWOTH;
                    break;
                case 'x':
                    if (who_mask & S_IRWXU) perm_mask |= S_IXUSR;
                    if (who_mask & S_IRWXG) perm_mask |= S_IXGRP;
                    if (who_mask & S_IRWXO) perm_mask |= S_IXOTH;
                    break;
            }
            ptr++;
        }
        
        /* Apply the operation */
        switch (op) {
            case '+':
                new_mode |= perm_mask;
                break;
            case '-':
                new_mode &= ~perm_mask;
                break;
            case '=':
                new_mode = (new_mode & ~who_mask) | perm_mask;
                break;
        }
        
        token = strtok(NULL, ",");
    }
    
    free(mode_copy);
    return new_mode;
}

/* Parse mode string (numeric or symbolic) */
static int parse_mode(const char *mode_str, mode_t *mode, int is_symbolic) {
    if (!mode_str) {
        *mode = (mode_t)-1;  /* No mode change */
        return 0;
    }
    
    if (is_numeric_mode(mode_str)) {
        *mode = parse_numeric_mode(mode_str);
        if (*mode == (mode_t)-1) {
            fprintf(stderr, "my_chown: invalid mode: '%s'\n", mode_str);
            return -1;
        }
    } else {
        /* For symbolic modes, we need the current mode, so we'll handle this in the main function */
        *mode = (mode_t)-2;  /* Special value indicating symbolic mode */
    }
    
    return 0;
}

/* Convert mode to string representation */
static const char *mode_to_string(mode_t mode) {
    static char mode_str[10];
    
    mode_str[0] = (mode & S_IRUSR) ? 'r' : '-';
    mode_str[1] = (mode & S_IWUSR) ? 'w' : '-';
    mode_str[2] = (mode & S_IXUSR) ? 'x' : '-';
    mode_str[3] = (mode & S_IRGRP) ? 'r' : '-';
    mode_str[4] = (mode & S_IWGRP) ? 'w' : '-';
    mode_str[5] = (mode & S_IXGRP) ? 'x' : '-';
    mode_str[6] = (mode & S_IROTH) ? 'r' : '-';
    mode_str[7] = (mode & S_IWOTH) ? 'w' : '-';
    mode_str[8] = (mode & S_IXOTH) ? 'x' : '-';
    mode_str[9] = '\0';
    
    return mode_str;
}

/* Print information about ownership and permission changes */
static void print_change(const char *path, uid_t old_uid, gid_t old_gid, uid_t new_uid, gid_t new_gid, 
                        mode_t old_mode, mode_t new_mode, struct options *opts) {
    struct passwd *old_pwd = getpwuid(old_uid);
    struct passwd *new_pwd = getpwuid(new_uid);
    struct group *old_grp = getgrgid(old_gid);
    struct group *new_grp = getgrgid(new_gid);
    
    int ownership_changed = (old_uid != new_uid || old_gid != new_gid);
    int permissions_changed = opts->change_perms && (old_mode != new_mode);
    
    if (!ownership_changed && !permissions_changed) {
        printf("ownership and permissions of '%s' retained", path);
    } else {
        printf("'%s' ", path);
    }
    
    if (ownership_changed) {
        printf("ownership changed from ");
        if (old_pwd) printf("%s", old_pwd->pw_name);
        else printf("%u", old_uid);
        
        printf(":");
        
        if (old_grp) printf("%s", old_grp->gr_name);
        else printf("%u", old_gid);
        
        printf(" to ");
        
        if (new_pwd) printf("%s", new_pwd->pw_name);
        else printf("%u", new_uid);
        
        printf(":");
        
        if (new_grp) printf("%s", new_grp->gr_name);
        else printf("%u", new_gid);
        
        if (permissions_changed) printf(", ");
    }
    
    if (permissions_changed) {
        printf("permissions changed from %s (%04o) to %s (%04o)", 
               mode_to_string(old_mode), old_mode & 07777,
               mode_to_string(new_mode), new_mode & 07777);
    }
    
    if (!ownership_changed && !permissions_changed) {
        printf(" as ");
        if (new_pwd) printf("%s", new_pwd->pw_name);
        else printf("%u", new_uid);
        
        printf(":");
        
        if (new_grp) printf("%s", new_grp->gr_name);
        else printf("%u", new_gid);
        
        if (opts->change_perms) {
            printf(" with permissions %s (%04o)", 
                   mode_to_string(new_mode), new_mode & 07777);
        }
    }
    
    printf("\n");
}

/* Change ownership and permissions of a single file/directory */
static int change_ownership_and_perms(const char *path, uid_t uid, gid_t gid, mode_t mode, struct options *opts) {
    struct stat st;
    int result;
    
    /* Get current file stats */
    if (opts->no_dereference) {
        result = lstat(path, &st);
    } else {
        result = stat(path, &st);
    }
    
    if (result != 0) {
        if (!opts->quiet) {
            perror(path);
        }
        return -1;
    }
    
    uid_t old_uid = st.st_uid;
    gid_t old_gid = st.st_gid;
    mode_t old_mode = st.st_mode;
    uid_t new_uid = (uid == (uid_t)-1) ? old_uid : uid;
    gid_t new_gid = (gid == (gid_t)-1) ? old_gid : gid;
    mode_t new_mode = old_mode;
    
    /* Handle symbolic mode parsing (needs current mode) */
    if (opts->change_perms && mode == (mode_t)-2) {
        /* This is a symbolic mode, we need to parse it with current mode */
        /* For now, we'll skip this case - it should be handled in main() */
        new_mode = old_mode;
    } else if (opts->change_perms && mode != (mode_t)-1) {
        new_mode = (old_mode & ~07777) | (mode & 07777);  /* Preserve file type bits */
    }
    
    /* Change ownership */
    if (uid != (uid_t)-1 || gid != (gid_t)-1) {
        if (opts->no_dereference) {
            result = lchown(path, new_uid, new_gid);
        } else {
            result = chown(path, new_uid, new_gid);
        }
        
        if (result != 0) {
            if (!opts->quiet) {
                fprintf(stderr, "my_chown: changing ownership of '%s': %s\n", 
                        path, strerror(errno));
            }
            return -1;
        }
    }
    
    /* Change permissions */
    if (opts->change_perms && mode != (mode_t)-1 && mode != (mode_t)-2) {
        result = chmod(path, new_mode);
        if (result != 0) {
            if (!opts->quiet) {
                fprintf(stderr, "my_chown: changing permissions of '%s': %s\n", 
                        path, strerror(errno));
            }
            return -1;
        }
    }
    
    /* Print verbose output */
    int ownership_changed = (old_uid != new_uid || old_gid != new_gid);
    int permissions_changed = opts->change_perms && (old_mode != new_mode);
    
    if (opts->verbose || (opts->changes_only && (ownership_changed || permissions_changed))) {
        print_change(path, old_uid, old_gid, new_uid, new_gid, old_mode, new_mode, opts);
    }
    
    return 0;
}

/* Recursively change ownership and permissions */
static int change_ownership_and_perms_recursive(const char *path, uid_t uid, gid_t gid, mode_t mode, struct options *opts) {
    struct stat st;
    DIR *dir;
    struct dirent *entry;
    char *full_path;
    int result = 0;
    
    /* First change the directory itself */
    if (change_ownership_and_perms(path, uid, gid, mode, opts) != 0) {
        result = -1;
    }
    
    /* Check if it's a directory */
    if (lstat(path, &st) != 0 || !S_ISDIR(st.st_mode)) {
        return result;
    }
    
    /* Open directory */
    dir = opendir(path);
    if (!dir) {
        if (!opts->quiet) {
            fprintf(stderr, "my_chown: cannot access '%s': %s\n", 
                    path, strerror(errno));
        }
        return -1;
    }
    
    /* Process each entry */
    while ((entry = readdir(dir)) != NULL) {
        /* Skip . and .. */
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }
        
        /* Build full path */
        size_t path_len = strlen(path);
        size_t name_len = strlen(entry->d_name);
        full_path = malloc(path_len + name_len + 2);
        if (!full_path) {
            fprintf(stderr, "my_chown: memory allocation failed\n");
            closedir(dir);
            return -1;
        }
        
        strcpy(full_path, path);
        if (path[path_len - 1] != '/') {
            strcat(full_path, "/");
        }
        strcat(full_path, entry->d_name);
        
        /* Recursively process */
        if (change_ownership_and_perms_recursive(full_path, uid, gid, mode, opts) != 0) {
            result = -1;
        }
        
        free(full_path);
    }
    
    closedir(dir);
    return result;
}

int main(int argc, char *argv[]) {
    struct options opts = {0};
    int opt;
    uid_t uid;
    gid_t gid;
    mode_t mode = (mode_t)-1;  /* No mode change by default */
    char *mode_str = NULL;
    int result = 0;
    
    static struct option long_options[] = {
        {"changes", no_argument, 0, 'c'},
        {"silent", no_argument, 0, 'f'},
        {"quiet", no_argument, 0, 'f'},
        {"verbose", no_argument, 0, 'v'},
        {"recursive", no_argument, 0, 'R'},
        {"no-dereference", no_argument, 0, 'h'},
        {"dereference", no_argument, 0, 'L'},
        {"help", no_argument, 0, 1000},
        {"version", no_argument, 0, 1001},
        {0, 0, 0, 0}
    };
    
    /* Parse command line options */
    while ((opt = getopt_long(argc, argv, "cfvRhL", long_options, NULL)) != -1) {
        switch (opt) {
            case 'c':
                opts.changes_only = 1;
                break;
            case 'f':
                opts.quiet = 1;
                break;
            case 'v':
                opts.verbose = 1;
                break;
            case 'R':
                opts.recursive = 1;
                break;
            case 'h':
                opts.no_dereference = 1;
                break;
            case 'L':
                opts.dereference = 1;
                break;
            case 1000:
                usage();
                exit(0);
            case 1001:
                printf("my_chown 1.0 (with chmod functionality)\n");
                exit(0);
            default:
                usage();
                exit(1);
        }
    }
    
    /* Check for conflicting options */
    if (opts.no_dereference && opts.dereference) {
        fprintf(stderr, "my_chown: cannot specify both -h and -L\n");
        exit(1);
    }
    
    /* Need at least owner and one file */
    if (optind + 1 >= argc) {
        fprintf(stderr, "my_chown: missing operand\n");
        usage();
        exit(1);
    }
    
    /* Parse owner:group specification */
    if (parse_owner_group(argv[optind], &uid, &gid) != 0) {
        exit(1);
    }
    optind++;
    
    /* Check if next argument is a mode specification */
    if (optind < argc && optind + 1 < argc) {
        /* Check if this looks like a mode (numeric or contains +, -, =) */
        char *potential_mode = argv[optind];
        if (is_numeric_mode(potential_mode) || 
            strchr(potential_mode, '+') || strchr(potential_mode, '-') || strchr(potential_mode, '=')) {
            mode_str = potential_mode;
            opts.change_perms = 1;
            optind++;
        }
    }
    
    /* Parse mode if provided */
    if (mode_str) {
        if (parse_mode(mode_str, &mode, 0) != 0) {
            exit(1);
        }
    }
    
    /* Need at least one file */
    if (optind >= argc) {
        fprintf(stderr, "my_chown: missing file operand\n");
        usage();
        exit(1);
    }
    
    /* Process each file */
    while (optind < argc) {
        mode_t file_mode = mode;
        
        /* Handle symbolic modes (need current file mode) */
        if (opts.change_perms && mode == (mode_t)-2) {
            struct stat st;
            if (stat(argv[optind], &st) == 0) {
                file_mode = parse_symbolic_mode(mode_str, st.st_mode);
                if (file_mode == (mode_t)-1) {
                    fprintf(stderr, "my_chown: invalid symbolic mode: '%s'\n", mode_str);
                    result = 1;
                    optind++;
                    continue;
                }
            } else {
                if (!opts.quiet) {
                    fprintf(stderr, "my_chown: cannot access '%s': %s\n", 
                            argv[optind], strerror(errno));
                }
                result = 1;
                optind++;
                continue;
            }
        }
        
        if (opts.recursive) {
            if (change_ownership_and_perms_recursive(argv[optind], uid, gid, file_mode, &opts) != 0) {
                result = 1;
            }
        } else {
            if (change_ownership_and_perms(argv[optind], uid, gid, file_mode, &opts) != 0) {
                result = 1;
            }
        }
        optind++;
    }
    
    return result;
}
