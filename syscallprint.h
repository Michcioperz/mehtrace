#ifndef MEHTRACE_SCPRINT_H
#define MEHTRACE_SCPRINT_H
#include <sys/types.h>
#include <sys/user.h>
void init_printfd(void);
void print_syscall(pid_t child, struct user_regs_struct *regs, int isexit);
#endif // MEHTRACE_SCPRINT_H
