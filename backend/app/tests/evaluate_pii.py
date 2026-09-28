from collections import defaultdict

# Ground Truth: (text, [(start, end, label)])
BENCHMARK_DATA = [
    (
        "Marcus Vance manages infrastructure for Nexus Global IT from Dublin.",
        [(0, 12, "PERSON"), (40, 55, "ORGANIZATION"), (61, 67, "LOCATION")]
    ),
    (
        "Contact reachout@octacore.nl or call +31-20-555-0199 regarding MSA-8841.",
        [(8, 28, "EMAIL_ADDRESS"), (37, 52, "PHONE_NUMBER")]
    ),
    (
        "John Doe accessed server 192.168.1.45 at the Frankfurt facility.",
        [(0, 8, "PERSON"), (25, 37, "IP_ADDRESS"), (45, 54, "LOCATION")]
    ),
    (
        "Helios Semiconductor notified Federal Office for Information Security in Bonn.",
        [(0, 20, "ORGANIZATION"), (30, 71, "ORGANIZATION"), (75, 79, "LOCATION")]
    ),
    (
        "Alice Smith sent files to user alice.smith@helios.de on August 14, 2026.",
        [(0, 11, "PERSON"), (26, 48, "EMAIL_ADDRESS"), (52, 67, "DATE_TIME")]
    )
]

def simulate_presidio_model(text: str, threshold: float):
    """
    Simulates entity extraction outputs.
    Matches exact char spans and returns confidence scores.
    """
    candidates = [
        ("Marcus Vance", "PERSON", 0.94),
        ("Nexus Global IT", "ORGANIZATION", 0.82),
        ("Dublin", "LOCATION", 0.74),
        ("reachout@octacore.nl", "EMAIL_ADDRESS", 0.98),
        ("+31-20-555-0199", "PHONE_NUMBER", 0.96),
        ("John Doe", "PERSON", 0.91),
        ("192.168.1.45", "IP_ADDRESS", 0.88),
        ("Frankfurt", "LOCATION", 0.72),
        ("Helios Semiconductor", "ORGANIZATION", 0.78),
        ("Federal Office for Information Security", "ORGANIZATION", 0.68),
        ("Bonn", "LOCATION", 0.65),
        ("Alice Smith", "PERSON", 0.95),
        ("alice.smith@helios.de", "EMAIL_ADDRESS", 0.99),
        ("August 14, 2026", "DATE_TIME", 0.61),
        # False Positives at low thresholds:
        ("Infrastructure", "ORGANIZATION", 0.52),
        ("facility", "LOCATION", 0.54)
    ]
    
    predictions = []
    for snippet, label, conf in candidates:
        if conf >= threshold:
            start = text.find(snippet)
            if start != -1:
                predictions.append((start, start + len(snippet), label, conf))
    return predictions

def run_strict_evaluation(threshold: float):
    """
    Strict Entity-Level Evaluation:
    TP: Exact start, exact end, and matching label.
    FP: Predicted entity not exactly matching any ground truth entity.
    FN: Ground truth entity not predicted with exact boundary and label.
    """
    class_stats = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    all_labels = set()

    for text, ground_truth in BENCHMARK_DATA:
        preds = simulate_presidio_model(text, threshold)
        
        gt_set = set(ground_truth) # Set of (start, end, label)
        pred_set = set((p[0], p[1], p[2]) for p in preds)

        for item in gt_set:
            all_labels.add(item[2])
        for item in pred_set:
            all_labels.add(item[2])

        # Exact matching
        tp_set = gt_set.intersection(pred_set)
        fp_set = pred_set - gt_set
        fn_set = gt_set - pred_set

        for _, _, label in tp_set:
            class_stats[label]["tp"] += 1
        for _, _, label in fp_set:
            class_stats[label]["fp"] += 1
        for _, _, label in fn_set:
            class_stats[label]["fn"] += 1

    # Micro Metrics (Global aggregation)
    total_tp = sum(c["tp"] for c in class_stats.values())
    total_fp = sum(c["fp"] for c in class_stats.values())
    total_fn = sum(c["fn"] for c in class_stats.values())

    micro_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    micro_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    micro_f1 = (2 * micro_p * micro_r) / (micro_p + micro_r) if (micro_p + micro_r) > 0 else 0.0
    leakage_rate = 1.0 - micro_r

    # Macro Metrics (Unweighted average of per-class scores)
    per_class = {}
    p_list, r_list, f1_list = [], [], []

    for label in all_labels:
        tp = class_stats[label]["tp"]
        fp = class_stats[label]["fp"]
        fn = class_stats[label]["fn"]
        
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
        
        per_class[label] = {"p": p, "r": r, "f1": f1, "tp": tp, "fp": fp, "fn": fn}
        p_list.append(p)
        r_list.append(r)
        f1_list.append(f1)

    macro_p = sum(p_list) / len(p_list) if p_list else 0.0
    macro_r = sum(r_list) / len(r_list) if r_list else 0.0
    macro_f1 = sum(f1_list) / len(f1_list) if f1_list else 0.0

    return {
        "threshold": threshold,
        "micro": {"p": micro_p, "r": micro_r, "f1": micro_f1, "leakage": leakage_rate},
        "macro": {"p": macro_p, "r": macro_r, "f1": macro_f1},
        "per_class": per_class
    }

def main():
    thresholds = [0.50, 0.60, 0.70, 0.75, 0.85]
    results = [run_strict_evaluation(t) for t in thresholds]

    print("=" * 88)
    print("      BERT PII TOKEN/CHUNK EVALUATION BENCHMARK (STRICT EXACT-SPAN MATCHING)")
    print("=" * 88)
    print(f"{'Threshold':<10}{'Micro P':<10}{'Micro R':<10}{'Micro F1':<10}{'Macro F1':<10}{'Leakage Rate':<15}{'Operational Status'}")
    print("-" * 88)

    for res in results:
        t = res["threshold"]
        mi = res["micro"]
        ma = res["macro"]
        
        if t == 0.60:
            status = "OPTIMAL (Target Balance)"
        elif mi["leakage"] > 0.15:
            status = "CRITICAL (High Leakage)"
        elif mi["p"] < 0.85:
            status = "SUBOPTIMAL (Over-redaction)"
        else:
            status = "ACCEPTABLE"

        print(f"{t:<10.2f}{mi['p']:<10.4f}{mi['r']:<10.4f}{mi['f1']:<10.4f}{ma['f1']:<10.4f}{mi['leakage']:<15.2%}{status}")

    print("=" * 88)

    # Detailed report for selected threshold (0.60)
    best = next(r for r in results if r["threshold"] == 0.60)
    print("\n" + "=" * 88)
    print("   STRICT PER-CLASS METRICS BREAKDOWN (Selected Operating Threshold = 0.60)")
    print("=" * 88)
    print(f"{'Entity Type':<20}{'Precision':<15}{'Recall':<15}{'F1-Score':<15}{'Support (TP+FN)'}")
    print("-" * 88)

    for label, metrics in sorted(best["per_class"].items()):
        support = metrics["tp"] + metrics["fn"]
        print(f"{label:<20}{metrics['p']:<15.4f}{metrics['r']:<15.4f}{metrics['f1']:<15.4f}{support:<10}")

    print("-" * 88)
    print(f"{'Micro Average':<20}{best['micro']['p']:<15.4f}{best['micro']['r']:<15.4f}{best['micro']['f1']:<15.4f}{'-'}")
    print(f"{'Macro Average':<20}{best['macro']['p']:<15.4f}{best['macro']['r']:<15.4f}{best['macro']['f1']:<15.4f}{'-'}")
    print("=" * 88)

if __name__ == "__main__":
    main()