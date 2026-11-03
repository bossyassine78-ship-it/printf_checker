#!/usr/bin/env python3
"""Quick differential evaluator for the 42 ft_printf mandatory part.

Usage:
    python3 ft_printf_eval.py /path/to/student/ft_printf
    python3 ft_printf_eval.py /path/to/student/ft_printf --bonus --memory

It rebuilds the project, performs a few subject-file checks, then compares the
student's ft_printf against libc printf in the *same process*.  Capturing both
calls in one process is important: %p receives the exact same pointer value.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


RUNNER_SOURCE = r'''#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <unistd.h>

#include "ft_printf.h"

#define BUFFER_CAPACITY 8192

typedef struct s_capture
{
	unsigned char	bytes[BUFFER_CAPACITY];
	size_t			len;
	int				ret;
}t_capture;

/* Calls libc printf or ft_printf with identical arguments in one process. */
static int	invoke_case(int id, int use_ft)
{
	int	value;

	value = 42;
	if (id == 0)
	{
		if (use_ft)
			return (ft_printf("plain text"));
		return (printf("plain text"));
	}
	if (id == 1)
	{
		if (use_ft)
			return (ft_printf("begin %% end"));
		return (printf("begin %% end"));
	}
	if (id == 2)
	{
		if (use_ft)
			return (ft_printf("[%c]", 'A'));
		return (printf("[%c]", 'A'));
	}
	if (id == 3)
	{
		if (use_ft)
			return (ft_printf("A%cB", 0));
		return (printf("A%cB", 0));
	}
	if (id == 4)
	{
		if (use_ft)
			return (ft_printf("[%c]", 255));
		return (printf("[%c]", 255));
	}
	if (id == 5)
	{
		if (use_ft)
			return (ft_printf("s=[%s]", ""));
		return (printf("s=[%s]", ""));
	}
	if (id == 6)
	{
		if (use_ft)
			return (ft_printf("s=[%s]", "hello"));
		return (printf("s=[%s]", "hello"));
	}
	if (id == 7)
	{
		if (use_ft)
			return (ft_printf("s=[%s]", "100% done"));
		return (printf("s=[%s]", "100% done"));
	}
	if (id == 8)
	{
		if (use_ft)
			return (ft_printf("p=[%p]", (void *)&value));
		return (printf("p=[%p]", (void *)&value));
	}
	if (id == 9)
	{
		if (use_ft)
			return (ft_printf("p=[%p]", (void *)0));
		return (printf("p=[%p]", (void *)0));
	}
	if (id == 10)
	{
		if (use_ft)
			return (ft_printf("d=%d", 0));
		return (printf("d=%d", 0));
	}
	if (id == 11)
	{
		if (use_ft)
			return (ft_printf("d=%d", 42));
		return (printf("d=%d", 42));
	}
	if (id == 12)
	{
		if (use_ft)
			return (ft_printf("d=%d", -42));
		return (printf("d=%d", -42));
	}
	if (id == 13)
	{
		if (use_ft)
			return (ft_printf("d=%d", INT_MAX));
		return (printf("d=%d", INT_MAX));
	}
	if (id == 14)
	{
		if (use_ft)
			return (ft_printf("d=%d", INT_MIN));
		return (printf("d=%d", INT_MIN));
	}
	if (id == 15)
	{
		if (use_ft)
			return (ft_printf("i=%i", 0));
		return (printf("i=%i", 0));
	}
	if (id == 16)
	{
		if (use_ft)
			return (ft_printf("i=%i", -42));
		return (printf("i=%i", -42));
	}
	if (id == 17)
	{
		if (use_ft)
			return (ft_printf("i=%i", INT_MAX));
		return (printf("i=%i", INT_MAX));
	}
	if (id == 18)
	{
		if (use_ft)
			return (ft_printf("i=%i", INT_MIN));
		return (printf("i=%i", INT_MIN));
	}
	if (id == 19)
	{
		if (use_ft)
			return (ft_printf("u=%u", 0U));
		return (printf("u=%u", 0U));
	}
	if (id == 20)
	{
		if (use_ft)
			return (ft_printf("u=%u", 42U));
		return (printf("u=%u", 42U));
	}
	if (id == 21)
	{
		if (use_ft)
			return (ft_printf("u=%u", UINT_MAX));
		return (printf("u=%u", UINT_MAX));
	}
	if (id == 22)
	{
		if (use_ft)
			return (ft_printf("u=%u", 2147483648U));
		return (printf("u=%u", 2147483648U));
	}
	if (id == 23)
	{
		if (use_ft)
			return (ft_printf("x=%x", 0U));
		return (printf("x=%x", 0U));
	}
	if (id == 24)
	{
		if (use_ft)
			return (ft_printf("x=%x", 42U));
		return (printf("x=%x", 42U));
	}
	if (id == 25)
	{
		if (use_ft)
			return (ft_printf("x=%x", 0xabcdefU));
		return (printf("x=%x", 0xabcdefU));
	}
	if (id == 26)
	{
		if (use_ft)
			return (ft_printf("x=%x", UINT_MAX));
		return (printf("x=%x", UINT_MAX));
	}
	if (id == 27)
	{
		if (use_ft)
			return (ft_printf("X=%X", 0U));
		return (printf("X=%X", 0U));
	}
	if (id == 28)
	{
		if (use_ft)
			return (ft_printf("X=%X", 42U));
		return (printf("X=%X", 42U));
	}
	if (id == 29)
	{
		if (use_ft)
			return (ft_printf("X=%X", 0xabcdefU));
		return (printf("X=%X", 0xabcdefU));
	}
	if (id == 30)
	{
		if (use_ft)
			return (ft_printf("X=%X", UINT_MAX));
		return (printf("X=%X", UINT_MAX));
	}
	if (id == 31)
	{
		if (use_ft)
			return (ft_printf("c=%c s=%s p=%p d=%d i=%i u=%u x=%x X=%X %%",
					'Z', "hi", (void *)&value, -42, 42, UINT_MAX, 0xabcU, 0xabcU));
		return (printf("c=%c s=%s p=%p d=%d i=%i u=%u x=%x X=%X %%",
				'Z', "hi", (void *)&value, -42, 42, UINT_MAX, 0xabcU, 0xabcU));
	}
	if (id == 32)
	{
		if (use_ft)
			return (ft_printf("%d%i%u%x%X%c%s%%", -1, 2, UINT_MAX,
					0x10U, 0x10U, '!', "end"));
		return (printf("%d%i%u%x%X%c%s%%", -1, 2, UINT_MAX,
				0x10U, 0x10U, '!', "end"));
	}
	if (id == 33)
	{
		if (use_ft)
			return (ft_printf("[%s][%c][%d]", "a", '\n', -1));
		return (printf("[%s][%c][%d]", "a", '\n', -1));
	}
	if (id == 34)
	{
		if (use_ft)
			return (ft_printf("%%%%%%"));
		return (printf("%%%%%%"));
	}
	/* This is compared to the current libc but is not ISO C defined. */
	if (id == 35)
	{
		if (use_ft)
			return (ft_printf("null=[%s]", (char *)0));
		return (printf("null=[%s]", (char *)0));
	}
	/* Optional bonus probes. */
	if (id == 36)
	{
		if (use_ft)
			return (ft_printf("[%5d][%-5d][%05d]", 42, 42, -42));
		return (printf("[%5d][%-5d][%05d]", 42, 42, -42));
	}
	if (id == 37)
	{
		if (use_ft)
			return (ft_printf("[%.5d][%8.5d][%08u]", -42, 42, 42U));
		return (printf("[%.5d][%8.5d][%08u]", -42, 42, 42U));
	}
	if (id == 38)
	{
		if (use_ft)
			return (ft_printf("[%+d][% d][%+i]", 42, 42, -42));
		return (printf("[%+d][% d][%+i]", 42, 42, -42));
	}
	if (id == 39)
	{
		if (use_ft)
			return (ft_printf("[%#x][%#X][%#08x]", 0x2aU, 0x2aU, 0x2aU));
		return (printf("[%#x][%#X][%#08x]", 0x2aU, 0x2aU, 0x2aU));
	}
	if (id == 40)
	{
		if (use_ft)
			return (ft_printf("[%10s][%-10s][%.3s][%5c][%-5c]",
					"abc", "abc", "abcdef", 'A', 'B'));
		return (printf("[%10s][%-10s][%.3s][%5c][%-5c]",
				"abc", "abc", "abcdef", 'A', 'B'));
	}
	if (id == 41)
	{
		if (use_ft)
			return (ft_printf("[%-08d][% 08d][%#10X]", 42, 42, 0xABU));
		return (printf("[%-08d][% 08d][%#10X]", 42, 42, 0xABU));
	}
	return (-424242);
}

static int	capture_case(int id, int use_ft, t_capture *capture)
{
	FILE	*tmp;
	int		saved_stdout;
	int		fd;
	long	end;

	tmp = tmpfile();
	if (tmp == NULL)
		return (-1);
	saved_stdout = -1;
	if (fflush(stdout) == EOF)
		goto failure;
	saved_stdout = dup(STDOUT_FILENO);
	if (saved_stdout < 0)
		goto failure;
	fd = fileno(tmp);
	if (dup2(fd, STDOUT_FILENO) < 0)
		goto failure;
	capture->ret = invoke_case(id, use_ft);
	if (fflush(stdout) == EOF)
		goto failure;
	if (dup2(saved_stdout, STDOUT_FILENO) < 0)
		goto failure;
	close(saved_stdout);
	saved_stdout = -1;
	if (fseek(tmp, 0L, SEEK_END) != 0)
		goto failure;
	end = ftell(tmp);
	if (end < 0 || end > BUFFER_CAPACITY)
		goto failure;
	if (fseek(tmp, 0L, SEEK_SET) != 0)
		goto failure;
	capture->len = fread(capture->bytes, 1, (size_t)end, tmp);
	if (capture->len != (size_t)end || ferror(tmp))
		goto failure;
	fclose(tmp);
	return (0);
failure:
	if (saved_stdout >= 0)
	{
		fflush(stdout);
		dup2(saved_stdout, STDOUT_FILENO);
		close(saved_stdout);
	}
	fclose(tmp);
	return (-1);
}

static void	print_hex(const unsigned char *bytes, size_t len)
{
	size_t	i;

	i = 0;
	while (i < len)
	{
		fprintf(stderr, "%02x", (unsigned int)bytes[i]);
		i++;
	}
}

int	main(int argc, char **argv)
{
	t_capture	standard;
	t_capture	student;
	int			id;

	if (argc != 2)
		return (3);
	id = atoi(argv[1]);
	if (capture_case(id, 0, &standard) != 0
		|| capture_case(id, 1, &student) != 0)
	{
		fprintf(stderr, "CAPTURE_ERROR\n");
		return (3);
	}
	if (standard.ret == student.ret && standard.len == student.len
		&& memcmp(standard.bytes, student.bytes, standard.len) == 0)
		return (0);
	fprintf(stderr, "STD_RET=%d\nFT_RET=%d\nSTD_HEX=", standard.ret, student.ret);
	print_hex(standard.bytes, standard.len);
	fprintf(stderr, "\nFT_HEX=");
	print_hex(student.bytes, student.len);
	fprintf(stderr, "\n");
	return (1);
}
'''


@dataclass(frozen=True)
class Case:
    case_id: int
    label: str
    tier: str = "mandatory"


CASES = [
    Case(0, "plain literal"),
    Case(1, "literal percent (%%)"),
    Case(2, "%c: normal character"),
    Case(3, "%c: NUL byte and return count"),
    Case(4, "%c: byte 255"),
    Case(5, "%s: empty string"),
    Case(6, "%s: normal string"),
    Case(7, "%s: percent inside argument"),
    Case(8, "%p: non-NULL pointer"),
    Case(9, "%p: NULL pointer"),
    Case(10, "%d: zero"),
    Case(11, "%d: positive"),
    Case(12, "%d: negative"),
    Case(13, "%d: INT_MAX"),
    Case(14, "%d: INT_MIN"),
    Case(15, "%i: zero"),
    Case(16, "%i: negative"),
    Case(17, "%i: INT_MAX"),
    Case(18, "%i: INT_MIN"),
    Case(19, "%u: zero"),
    Case(20, "%u: positive"),
    Case(21, "%u: UINT_MAX"),
    Case(22, "%u: high unsigned value"),
    Case(23, "%x: zero"),
    Case(24, "%x: normal"),
    Case(25, "%x: lowercase letters"),
    Case(26, "%x: UINT_MAX"),
    Case(27, "%X: zero"),
    Case(28, "%X: normal"),
    Case(29, "%X: uppercase letters"),
    Case(30, "%X: UINT_MAX"),
    Case(31, "all conversions in one call"),
    Case(32, "consecutive conversions"),
    Case(33, "newline / mixed return count"),
    Case(34, "three consecutive %% conversions"),
    Case(35, "%s: NULL (glibc compatibility only)", "compat"),
]

BONUS_CASES = [
    Case(36, "width / left align / zero pad", "bonus"),
    Case(37, "precision / width / unsigned zero pad", "bonus"),
    Case(38, "plus and space flags", "bonus"),
    Case(39, "hash flag and hash+zero+width", "bonus"),
    Case(40, "string and character width / precision", "bonus"),
    Case(41, "combined bonus flags", "bonus"),
]


def command(cmd: list[str], cwd: Path, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )


def show_build_failure(proc: subprocess.CompletedProcess[str]) -> None:
    print("\n[BUILD FAILED] make re did not finish successfully.")
    if proc.stdout.strip():
        print("--- make stdout ---\n" + proc.stdout.rstrip())
    if proc.stderr.strip():
        print("--- make stderr ---\n" + proc.stderr.rstrip())


def first_line(path: Path) -> str:
    with path.open(encoding="utf-8", errors="replace") as handle:
        return handle.readline().rstrip("\n")


def static_checks(project: Path) -> tuple[list[tuple[str, str]], list[str]]:
    """Return visible checks and hard errors that should stop test compilation."""
    checks: list[tuple[str, str]] = []
    hard_errors: list[str] = []
    makefile = project / "Makefile"
    header = project / "ft_printf.h"
    readme = project / "README.md"

    for target in (makefile, header):
        if target.is_file():
            checks.append(("PASS", f"{target.name} exists"))
        else:
            checks.append(("FAIL", f"missing required {target.name}"))
            hard_errors.append(f"missing {target.name}")

    if makefile.is_file():
        text = makefile.read_text(encoding="utf-8", errors="replace")
        name_ok = re.search(r"(?m)^\s*NAME\s*[:?+]?=", text) is not None
        targets_ok = all(
            re.search(rf"(?m)^\s*{name}\s*:", text) is not None
            for name in ("all", "clean", "fclean", "re")
        )
        checks.append(("PASS" if name_ok else "FAIL", "Makefile defines NAME"))
        checks.append(("PASS" if targets_ok else "FAIL", "Makefile has all/clean/fclean/re rules"))
        if not name_ok or not targets_ok:
            hard_errors.append("incomplete Makefile requirements")

    if header.is_file():
        text = header.read_text(encoding="utf-8", errors="replace")
        prototype_ok = re.search(
            r"\bint\s+ft_printf\s*\(\s*(?:const\s+char|char\s+const)\s*\*",
            text,
        ) is not None
        checks.append(("PASS" if prototype_ok else "FAIL", "ft_printf.h declares int ft_printf(const char *, ...)"))
        if not prototype_ok:
            hard_errors.append("missing or wrong ft_printf prototype")

    if not readme.is_file():
        checks.append(("FAIL", "missing required README.md"))
    else:
        intro = first_line(readme).strip()
        intro_ok = re.match(
            r"^(\*|_)(This project has been created as part of the 42 curriculum by .+)\1$",
            intro,
        ) is not None
        readme_text = readme.read_text(encoding="utf-8", errors="replace")
        sections_ok = all(
            re.search(rf"(?im)^#+\s*{section}\s*$", readme_text) is not None
            for section in ("Description", "Instructions", "Resources")
        )
        algo_ok = re.search(r"(?i)algorithm", readme_text) is not None and re.search(
            r"(?i)data\s+structure", readme_text
        ) is not None
        checks.append(("PASS" if intro_ok else "FAIL", "README first line has the required italicized declaration"))
        checks.append(("PASS" if sections_ok else "FAIL", "README has Description, Instructions, Resources"))
        checks.append(("PASS" if algo_ok else "WARN", "README mentions algorithm and data structure justification"))
    return checks, hard_errors


def decode_mismatch(stderr: str) -> str:
    values: dict[str, str] = {}
    for line in stderr.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    if not {"STD_RET", "FT_RET", "STD_HEX", "FT_HEX"}.issubset(values):
        return stderr.strip()[-600:] or "no diagnostic returned"

    def pretty(hex_value: str) -> str:
        try:
            raw = bytes.fromhex(hex_value)
            text = repr(raw)
            return text if len(text) <= 170 else text[:167] + "..."
        except ValueError:
            return "<invalid hex>"

    return (
        f"return libc={values['STD_RET']}, ft={values['FT_RET']}; "
        f"libc={pretty(values['STD_HEX'])}; ft={pretty(values['FT_HEX'])}"
    )


def run_memory_probe(exe: Path, project: Path) -> tuple[str, str]:
    valgrind = shutil.which("valgrind")
    if not valgrind:
        return "WARN", "valgrind not installed; skipped --memory probe"
    proc = command(
        [
            valgrind,
            "--quiet",
            "--leak-check=full",
            "--show-leak-kinds=all",
            "--errors-for-leak-kinds=all",
            "--error-exitcode=97",
            str(exe),
            "31",
        ],
        project,
        timeout=15,
    )
    if proc.returncode == 0:
        return "PASS", "valgrind mixed-conversion probe"
    if proc.returncode == 97:
        return "FAIL", "valgrind found an invalid access or leak in the mixed probe"
    return "WARN", f"valgrind probe could not conclude (exit {proc.returncode})"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Differential checker for a 42 ft_printf project."
    )
    parser.add_argument("project", nargs="?", default=".", help="student project directory (default: .)")
    parser.add_argument("--bonus", action="store_true", help="also run focused flag/width/precision probes")
    parser.add_argument("--memory", action="store_true", help="run one Valgrind probe when Valgrind is available")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        print(f"ERROR: not a directory: {project}", file=sys.stderr)
        return 2
    if shutil.which("make") is None or shutil.which("cc") is None or shutil.which("ar") is None:
        print("ERROR: make, cc, and ar must be available in PATH.", file=sys.stderr)
        return 2

    print(f"Project: {project}")
    checks, hard_errors = static_checks(project)
    subject_failures = 0
    for state, detail in checks:
        print(f"[{state}] {detail}")
        if state == "FAIL":
            subject_failures += 1
    if hard_errors:
        print("\nCannot compile the differential runner until the hard failures above are fixed.")
        return 1

    try:
        build = command(["make", "re"], project, timeout=45)
    except subprocess.TimeoutExpired:
        print("[BUILD FAILED] make re timed out after 45 seconds.")
        return 1
    if build.returncode != 0:
        show_build_failure(build)
        return 1
    print("[PASS] make re")

    archive = project / "libftprintf.a"
    if not archive.is_file():
        print("[FAIL] make re succeeded but libftprintf.a is not at the project root.")
        return 1
    if archive.read_bytes()[:8] != b"!<arch>\n":
        print("[FAIL] libftprintf.a is not an ar archive.")
        return 1
    listed = command(["ar", "t", str(archive)], project)
    if listed.returncode != 0 or not listed.stdout.strip():
        print("[FAIL] ar cannot read libftprintf.a, or the archive is empty.")
        return 1
    print("[PASS] libftprintf.a is a non-empty ar archive")

    makefile_text = (project / "Makefile").read_text(encoding="utf-8", errors="replace")
    if "libtool" in makefile_text.lower():
        print("[FAIL] Makefile mentions forbidden libtool.")
        subject_failures += 1
    elif re.search(r"(?m)^\s*AR\s*[:?+]?=", makefile_text) and "$(AR)" in makefile_text:
        print("[PASS] Makefile uses AR / ar to create the archive")
    elif re.search(r"(?m)(^|\s)ar\s+[a-zA-Z]*r", makefile_text):
        print("[PASS] Makefile uses ar to create the archive")
    else:
        print("[WARN] could not confirm an ar command from `make -n re`")

    before = archive.stat().st_mtime_ns
    try:
        passive_make = command(["make"], project, timeout=30)
    except subprocess.TimeoutExpired:
        print("[FAIL] plain make timed out after 30 seconds.")
        return 1
    if passive_make.returncode != 0:
        print("[FAIL] plain make fails after make re.")
        return 1
    after = archive.stat().st_mtime_ns
    if after == before:
        print("[PASS] plain make does not relink libftprintf.a")
    else:
        print("[FAIL] plain make relinks libftprintf.a unnecessarily")
        subject_failures += 1

    with tempfile.TemporaryDirectory(prefix="ft_printf_eval_") as temp_dir:
        temp = Path(temp_dir)
        runner_c = temp / "runner.c"
        runner = temp / "runner"
        runner_c.write_text(RUNNER_SOURCE, encoding="utf-8")
        compile_result = command(
            [
                "cc",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-Wno-format",
                "-std=c99",
                "-I",
                str(project),
                str(runner_c),
                str(archive),
                "-o",
                str(runner),
            ],
            project,
            timeout=30,
        )
        if compile_result.returncode != 0:
            print("[FAIL] could not link a caller against libftprintf.a")
            print(compile_result.stderr.rstrip())
            return 1
        print("[PASS] external program links against ft_printf")

        selected_cases = CASES + (BONUS_CASES if args.bonus else [])
        mandatory_failures = 0
        bonus_failures = 0
        compat_failures = 0
        passed = 0
        print("\n--- libc differential tests ---")
        for case in selected_cases:
            try:
                result = command([str(runner), str(case.case_id)], project, timeout=3)
            except subprocess.TimeoutExpired:
                print(f"[FAIL] {case.label}: timeout / probable infinite loop")
                if case.tier == "mandatory":
                    mandatory_failures += 1
                elif case.tier == "bonus":
                    bonus_failures += 1
                else:
                    compat_failures += 1
                continue
            if result.returncode == 0:
                print(f"[PASS] {case.label}")
                passed += 1
                continue
            if result.returncode < 0:
                detail = f"crashed with signal {-result.returncode}"
            else:
                detail = decode_mismatch(result.stderr)
            state = "WARN" if case.tier == "compat" else "FAIL"
            print(f"[{state}] {case.label}: {detail}")
            if case.tier == "mandatory":
                mandatory_failures += 1
            elif case.tier == "bonus":
                bonus_failures += 1
            else:
                compat_failures += 1

        if args.memory and mandatory_failures == 0:
            state, detail = run_memory_probe(runner, project)
            print(f"[{state}] {detail}")

    mandatory_count = sum(case.tier == "mandatory" for case in CASES)
    print("\n--- summary ---")
    print(f"subject-file checks: {subject_failures} failure(s)")
    print(f"mandatory: {mandatory_count - mandatory_failures}/{mandatory_count} passed")
    if args.bonus:
        print(f"bonus probes: {len(BONUS_CASES) - bonus_failures}/{len(BONUS_CASES)} passed")
    if compat_failures:
        print("compatibility note: libc's non-standard NULL %s behavior differed; do not use it alone to grade.")
    if mandatory_failures == 0 and subject_failures == 0:
        print("VERDICT: project passed this focused mandatory evaluation suite.")
        return 0
    if mandatory_failures == 0:
        print("VERDICT: output behavior passed, but subject requirement checks still failed.")
        return 1
    print("VERDICT: mandatory behavior has failures; inspect the lines above before passing the project.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
