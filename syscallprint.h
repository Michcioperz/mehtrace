#ifndef MEHTRACE_SCPRINT_H
#define MEHTRACE_SCPRINT_H
#include <sys/types.h>
#include <sys/user.h>
void print_syscall(pid_t child, struct user_regs_struct *regs);
#endif // MEHTRACE_SCPRINT_H
