#include "syscallprint.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/user.h>
#include <sys/wait.h>
#include <unistd.h>

int mehtrace(pid_t child) {
  init_printfd();
  fprintf(stderr, "%d\n", waitpid(child, NULL, 0));
  if (ptrace(PTRACE_SETOPTIONS, child, NULL, PTRACE_O_EXITKILL)) {
    perror("failed to PTRACE_SETOPTIONS");
    return EXIT_FAILURE;
  }
  struct user_regs_struct regs;
  int isexit = 0;
  for (;; isexit = !isexit) {
    if (ptrace(PTRACE_SYSCALL, child, NULL, 0)) {
      perror("failed to PTRACE_SYSCALL");
      return EXIT_FAILURE;
    }
    waitpid(child, NULL, 0);
    if (ptrace(PTRACE_GETREGS, child, NULL, &regs)) {
      perror("failed to PTRACE_GETREGS");
      return EXIT_FAILURE;
    }
    print_syscall(child, &regs, isexit);
  }
}

int main(int argc, char *argv[]) {
  (void)argc;
  pid_t child = fork();
  switch (child) {
  case -1:
    perror("failed to fork");
    return EXIT_FAILURE;
  case 0:
    if (ptrace(PTRACE_TRACEME, 0, NULL, NULL)) {
      perror("failed to PTRACE_TRACEME");
      return EXIT_FAILURE;
    }
    if (raise(SIGSTOP)) {
      perror("failed to raise SIGTRAP");
      return EXIT_FAILURE;
    }
    execvp(argv[1], &argv[1]);
    perror("failed to exec");
    return EXIT_FAILURE;
  default:
    return mehtrace(child);
  }
}
