#!/usr/bin/env python3
import json, warnings
with open('TABELLA_64.json') as f:
    calls = json.load(f)

check_ptr = 'if (childAddr == NULL) { fputs("NULL", stderr); return; } '

print_functions = {
        "dirfd": 'if ((int)childAddr == -100) fputs("AT_FDCWD", stderr); else fprintf(stderr, "%d", (int)childAddr);',
        "umode_t": 'fprintf(stderr, "%#3o", (mode_t)childAddr);',
        "size_t": 'fprintf(stderr, "%zu", (size_t)childAddr);',
        "u64": 'fprintf(stderr, "%llu", (uint64_t)childAddr);',
        "__u64": 'fprintf(stderr, "%llu", (uint64_t)childAddr);',
        "u32": 'fprintf(stderr, "%lu", (uint32_t)childAddr);',
        "__s32": 'fprintf(stderr, "%ld", (int32_t)childAddr);',
        "long": 'fprintf(stderr, "%ld", (long)childAddr);',
        "unsigned long": 'fprintf(stderr, "%lu", (unsigned long)childAddr);',
        "unsigned": 'fprintf(stderr, "%u", (unsigned)childAddr);',
        "unsigned int": 'fprintf(stderr, "%u", (unsigned int)childAddr);',
        "int": 'fprintf(stderr, "%d", (int)childAddr);',
        "void *": check_ptr+'fprintf(stderr, "%p", (void *)childAddr);',
        "char __user *": check_ptr+r'''
        char str[sizeof(childAddr)+1];
        str[sizeof(childAddr)] = 0;
        fputc('"', stderr);
        for (*((uint64_t *) str) = 0xFFFFFFFFFFFFFFFF; strlen(str) >= 8; childAddr += sizeof(childAddr)) {
            *((uint64_t *)str) = ptrace(PTRACE_PEEKTEXT, child, childAddr, NULL);
            for (char *ptr = &str[0]; *ptr != 0; ptr++) {
                switch (*ptr) {
                    case '\a': fputs("\\a",  stderr); break;
                    case '\b': fputs("\\b",  stderr); break;
                    case '\f': fputs("\\f",  stderr); break;
                    case '\n': fputs("\\n",  stderr); break;
                    case '\r': fputs("\\r",  stderr); break;
                    case '\t': fputs("\\t",  stderr); break;
                    case '"':  fputs("\\\"", stderr); break;
                    default:
                        if (isprint(*ptr))
                            fputc(*ptr, stderr);
                        else
                            fprintf(stderr, "\\x%x", *ptr);
                }
            }
        }
        fputc('"', stderr);''',
}
print_functions["const char __user *"] = print_functions["char __user *"]

print_function_idx = list(print_functions.keys())

type_overrides = dict(
    mmap=dict(addr="void *", fd="int"),
    mprotect=dict(start="void *"),
    munmap=dict(addr="void *"),
    brk=dict(brk="void *"),
    openat=dict(dfd="dirfd"),
)

missing_types = set()

arg_regs = ['rdi', 'rsi', 'rdx', 'r10', 'r8', 'r9']

for header in ['stdio.h', 'unistd.h', 'sys/types.h', 'stdint.h', 'ctype.h', 'sys/ptrace.h', 'string.h', 'sys/stat.h', 'fcntl.h']:
    print(f'#include <{header}>')
print('#include "syscallprint.h"')

print('''static char stderrbuf[4096];
void init_printfd(void) {
    setvbuf(stderr, stderrbuf, _IOLBF, sizeof(stderrbuf));
}''')

for i, tn in enumerate(print_function_idx):
    print(f'static void print_type_{i}(pid_t child, void *childAddr) {{ {print_functions[tn]} }}')

for nr, name, entrypoint, srcfile, args in calls.values():
    print(f'static void print_{name}(pid_t child, struct user_regs_struct *regs) {{')
    print(f'fputs("{name}(", stderr);')
    if args:
        for reg_i, arg in enumerate(args):
            arg_type = type_overrides.setdefault(name, {}).get(arg[1], arg[0])
            print(f'fputs("{arg[1]}=", stderr);')
            try:
                print(f'print_type_{print_function_idx.index(arg_type)}(child, (void*)regs->{arg_regs[reg_i]});')
            except ValueError:
                if arg_type not in missing_types:
                    missing_types.add(arg_type)
                    warnings.warn(f"Missing type: {arg_type!r}")
                print(f'fputs("{arg_type}", stderr);')
            print('fputs(",", stderr);')
    print('fputs(")", stderr);')
    print('}')

print('''
void print_syscall(pid_t child, struct user_regs_struct *regs, int isexit) {
  switch (regs->orig_rax) {
''')
for nr, name, entrypoint, srcfile, args in calls.values():
    print(f'case {nr}: print_{name}(child, regs); break;')
print('''
    default: fprintf(stderr, "unknown_syscall_%d(...)\\n", (unsigned int)regs->orig_rax);
  }
  if (isexit)
    fputs(" = ?\\n", stderr);
  else
    fprintf(stderr, " = %lld\\n", regs->rax);
}''')
