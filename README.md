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

## Usage

Clone this repository, then run the checker with the path to the student's
`ft_printf` project:

```bash
git clone https://github.com/bossyassine78-ship-it/printf_checker.git
cd printf_checker
./ft_printf_eval.py /path/to/student/ft_printf
```

From inside the student's repository, this also works:

```bash
/path/to/printf_checker/ft_printf_eval.py .
```

Run focused bonus probes:

```bash
./ft_printf_eval.py /path/to/student/ft_printf --bonus
```

Run the optional Valgrind mixed-conversion probe:

```bash
./ft_printf_eval.py /path/to/student/ft_printf --memory
```

The checker runs 35 strict mandatory differential tests for `cspdiuxX%`.
The `NULL` `%s` test is reported separately as a libc-compatibility check,
because its behavior is not defined by ISO C.
