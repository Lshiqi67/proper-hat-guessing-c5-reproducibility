# Dependencies

| Task | Required dependency | Tested here |
| --- | --- | --- |
| Restore, hash, validate catalogue, audit all CNF inputs | Python 3.11+ standard library | Python 3.13.0 on Windows |
| Replay existing certificates | Above, plus C# compiler/runtime | Windows .NET Framework 64-bit v4.0.30319 compiler |
| Optional original input generation / SAT search | python-sat==1.9.dev17 and six==1.17.0 | Historical dependency record; no new search in v2 packaging |

No third-party Python module is required by `tools/verify.py` or the fresh
input auditor. No prebuilt checker binary or third-party library is bundled in
the code ZIP. A new checker is compiled into each fresh replay output directory.
Alternative OS/compiler routes have not been tested by this packaging run.
