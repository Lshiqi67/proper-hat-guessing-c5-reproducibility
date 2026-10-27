"""生成完整 C5 合法染色猜帽模型的 DIMACS 文件；不调用求解器。"""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


def build(q, normalize=False):
    variables = [(i, a, b, g) for i in range(1, 6) for a in range(1, q + 1)
                 for b in range(1, q + 1) for g in range(1, q + 1) if g not in (a, b)]
    ids = {key: index for index, key in enumerate(variables, start=1)}
    clauses = []
    for i, a, b in itertools.product(range(1, 6), range(1, q + 1), range(1, q + 1)):
        group = [ids[i, a, b, g] for g in range(1, q + 1) if g not in (a, b)]
        clauses.append(group)
        clauses.extend([[-x, -y] for x, y in itertools.combinations(group, 2)])
    coverage_count = 0
    for c in itertools.product(range(1, q + 1), repeat=5):
        if all(c[i] != c[(i + 1) % 5] for i in range(5)):
            clauses.append([ids[i + 1, c[(i - 1) % 5], c[(i + 1) % 5], c[i]] for i in range(5)])
            coverage_count += 1
    if normalize:
        clauses.extend([[ids[1, 1, 1, 2]], [ids[1, 1, 2, 3]]])
    return variables, clauses, coverage_count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--q', type=int, choices=[4, 5], default=5)
    parser.add_argument('--normalize', action='store_true', help='加入两个已证明安全的颜色规范化单位子句')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    variables, clauses, coverage_count = build(args.q, args.normalize)
    args.output.mkdir(parents=True, exist_ok=True)
    cnf = 'c C5 proper-coloring hat game; generated, not solved\n'
    cnf += f'p cnf {len(variables)} {len(clauses)}\n'
    cnf += ''.join(' '.join(map(str, clause)) + ' 0\n' for clause in clauses)
    cnf_path = args.output / 'instance.cnf'
    cnf_path.write_text(cnf, encoding='ascii', newline='\n')
    mapping = {'q': args.q, '字段': ['玩家', '左邻颜色', '右邻颜色', '猜测颜色'],
               'variables': [{'id': index, 'i': i, 'a': a, 'b': b, 'g': g}
                             for index, (i, a, b, g) in enumerate(variables, start=1)]}
    map_path = args.output / 'variables.json'
    map_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    manifest = {'q': args.q, 'normalized': args.normalize, 'variables': len(variables),
                'exactly_one_groups': 5 * args.q ** 2, 'coverage_conditions': coverage_count,
                'cnf_clauses': len(clauses), 'solver_status': '未运行',
                'encoder_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'cnf_sha256': hashlib.sha256(cnf_path.read_bytes()).hexdigest(),
                'mapping_sha256': hashlib.sha256(map_path.read_bytes()).hexdigest(),
                '说明': 'CNF 文件不是求解结果；没有五色必胜证书或不可满足证书。'}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'已生成 q={args.q}：{len(variables)} 个变量，{len(clauses)} 个 CNF 子句；求解器未运行。')


if __name__ == '__main__':
    main()
