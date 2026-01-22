import argparse
import json
import pathlib
import re
from typing import Dict, List, Tuple


def find_section(text: str, start_markers: List[str], end_markers: List[str]) -> str:
    start_idx = -1
    for marker in start_markers:
        start_idx = text.find(marker)
        if start_idx != -1:
            start_idx += len(marker)
            break
    if start_idx == -1:
        return ""
    end_idx_candidates: List[int] = []
    for marker in end_markers:
        idx = text.find(marker, start_idx)
        if idx != -1:
            end_idx_candidates.append(idx)
    end_idx = min(end_idx_candidates) if end_idx_candidates else len(text)
    return text[start_idx:end_idx]


def normalize_letter(ch: str) -> str:
    mapping: Dict[str, str] = {
        "Ａ": "A",
        "Ｂ": "B",
        "Ｃ": "C",
        "Ｄ": "D",
        "Ｅ": "E",
        "Ｆ": "F",
        "Ｇ": "G",
        "Ｈ": "H",
    }
    return mapping.get(ch, ch)


def extract_answer(block: str) -> Tuple[str, str]:
    matches = list(re.finditer(r"（\s*([A-HＡ-Ｈ\s]+)\s*）", block))
    if not matches:
        return "", block
    m = matches[-1]
    raw = m.group(1)
    letters: List[str] = []
    for ch in raw:
        if ch.isspace():
            continue
        ch = normalize_letter(ch.upper())
        if "A" <= ch <= "H":
            letters.append(ch)
    answer = "".join(letters)
    cleaned = block[: m.start()] + block[m.end() :]
    return answer, cleaned


def parse_judge_section(text: str, prefix: str) -> List[Dict]:
    pattern = re.compile(r"(\d+)、（(√|×)）")
    items: List[Dict] = []
    matches = list(pattern.finditer(text))
    for i, match in enumerate(matches):
        qnum = match.group(1)
        sign = match.group(2)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        title = text[start:end].strip()
        title = title.lstrip("。 、，\n\r\t")
        title = title.strip()
        if not title:
            continue
        answer = "A" if sign == "√" else "B"
        item = {
            "id": f"{prefix}-J{qnum}",
            "title": title,
            "type": "judge",
            "option": ["正确", "错误"],
            "answer": answer,
            "analysis": "",
        }
        items.append(item)
    return items


def split_options(block: str) -> List[str]:
    m = re.search(r"[A-HＡ-Ｈ][、\.．]", block)
    if not m:
        return []
    options_text = block[m.start() :]
    parts = re.split(r"([A-HＡ-Ｈ][、\.．])", options_text)
    options: List[str] = []
    current_label = ""
    current_text = ""
    for part in parts:
        if not part:
            continue
        if re.fullmatch(r"[A-HＡ-Ｈ][、\.．]", part):
            if current_label:
                text_clean = current_text.strip()
                if text_clean:
                    options.append(text_clean)
            current_label = part
            current_text = ""
        else:
            current_text += part
    if current_label:
        text_clean = current_text.strip()
        if text_clean:
            options.append(text_clean)
    return options


def parse_choice_section(text: str, section_type: str, id_prefix: str, prefix: str) -> List[Dict]:
    pattern = re.compile(r"(\d+)[、\.．]")
    matches = list(pattern.finditer(text))
    items: List[Dict] = []
    for idx, m in enumerate(matches):
        qnum = m.group(1)
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        if not block:
            continue
        answer, without_answer = extract_answer(block)
        if not answer:
            continue
        options = split_options(without_answer)
        if not options:
            continue
        stem_end_match = re.search(r"[A-HＡ-Ｈ][、\.．]", without_answer)
        if stem_end_match:
            title = without_answer[: stem_end_match.start()]
        else:
            title = without_answer
        title = title.strip()
        if not title:
            continue
        qtype = section_type
        item = {
            "id": f"{prefix}-{id_prefix}{qnum}",
            "title": title,
            "type": qtype,
            "option": options,
            "answer": answer,
            "analysis": "",
        }
        items.append(item)
    return items


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        default=r"d:\code\github\aishuati\json\111.txt",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=r"d:\code\github\aishuati\json\111_all.json",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        default="2026Q1",
    )
    args = parser.parse_args()
    path = pathlib.Path(args.input)
    prefix = args.prefix
    text = path.read_text(encoding="utf-8", errors="ignore")
    judge_text = find_section(
        text,
        ["一、判断题"],
        ["二、选择题（单选题）", "二、选择题(单选题)", "二、单选题", "二、选择题"],
    )
    single_text = find_section(
        text,
        ["二、选择题（单选题）", "二、选择题(单选题)", "二、单选题", "二、选择题"],
        ["三、选择题（多选题）", "三、选择题(多选题)", "三、多选题", "三、选择题"],
    )
    multi_text = find_section(
        text,
        ["三、选择题（多选题）", "三、选择题(多选题)", "三、多选题"],
        [],
    )
    judge_items = parse_judge_section(judge_text, prefix) if judge_text else []
    single_items = (
        parse_choice_section(single_text, "single", "S", prefix) if single_text else []
    )
    multi_items = (
        parse_choice_section(multi_text, "multi", "M", prefix) if multi_text else []
    )
    all_items = judge_items + single_items + multi_items
    out_all = pathlib.Path(args.output)
    out_all.write_text(
        json.dumps(all_items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"判断题数量: {len(judge_items)}")
    print(f"单选题数量: {len(single_items)}")
    print(f"多选题数量: {len(multi_items)}")
    print(f"总数量: {len(all_items)}")
    print(f"已生成: {out_all}")


if __name__ == "__main__":
    main()
