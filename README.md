# printf_checker

Focused evaluator for the 42 / 1337 `ft_printf` project.

It rebuilds a student project, checks the required files and archive, then
compares `ft_printf` with libc `printf` in the same process. It tests output
bytes and the return value, including an embedded NUL character and edge
integer values.

## Requirements

- `python3`
- `make`, `cc`, and `ar`
- Optional: `valgrind` for the memory probe

## Quick workflow

Clone the checker once into your Home directory:

```bash
git clone https://github.com/bossyassine78-ship-it/printf_checker.git ~/printf_checker
```

Then, when you need to evaluate a student, enter their `ft_printf` project:

```bash
cd /path/to/student/ft_printf
```

Run the mandatory checker from there:

```bash
python3 ~/printf_checker/ft_printf_eval.py .
```

The final `.` means: test the directory where you are currently located.

For the optional bonus probes:

```bash
python3 ~/printf_checker/ft_printf_eval.py . --bonus
```

For the optional Valgrind mixed-conversion probe:

```bash
python3 ~/printf_checker/ft_printf_eval.py . --memory
```

The checker runs 35 strict mandatory differential tests for `cspdiuxX%`.
The `NULL` `%s` test is reported separately as a libc-compatibility check,
because its behavior is not defined by ISO C.
