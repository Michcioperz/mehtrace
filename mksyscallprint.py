#!/usr/bin/env python3
import json, warnings
with open('TABELLA_64.json') as f:
    calls = json.load(f)

check_ptr = 'if (childAddr == NULL) return; '

print_functions = {
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
#        "char __user *": check_ptr+'char str[sizeof(childAddr)+1]; str[sizeof(childAddr)] = 0; for (void *data = 0xFFFFFFFFFFFFFFFF; 
}

print_function_idx = list(print_functions.keys())

missing_types = set()

arg_regs = ['rdi', 'rsi', 'rdx', 'r10', 'r8', 'r9']

for header in ['stdio.h', 'unistd.h', 'sys/types.h', 'stdint.h']:
    print(f'#include <{header}>')
print('#include "syscallprint.h"')

for i, tn in enumerate(print_function_idx):
    print(f'static void print_type_{i}(pid_t child, void *childAddr) {{ {print_functions[tn]} }}')

for nr, name, entrypoint, srcfile, args in calls.values():
    print(f'static void print_{name}(pid_t child, struct user_regs_struct *regs) {{')
    print(f'fputs("{name}(", stderr);')
    if args:
        for reg_i, arg in enumerate(args):
            print(f'fputs("{arg[1]}=", stderr);')
            try:
                print(f'print_type_{print_function_idx.index(arg[0])}(child, (void*)regs->{arg_regs[reg_i]});')
            except ValueError:
                if arg[0] not in missing_types:
                    missing_types.add(arg[0])
                    warnings.warn(f"Missing type: {arg[0]!r}")
                print(f'fputs("{arg[0]}", stderr);')
            print('fputs(",", stderr);')
    print(f'fputs(")\\n", stderr);')
    print('}')

print('void print_syscall(pid_t child, struct user_regs_struct *regs) {')
print('switch (regs->orig_rax) {')
for nr, name, entrypoint, srcfile, args in calls.values():
    print(f'case {nr}: print_{name}(child, regs); break;')
print(f'default: fprintf(stderr, "unknown_syscall_%d(...)\\n", (unsigned int)regs->orig_rax);')
print('}')
print('}')
