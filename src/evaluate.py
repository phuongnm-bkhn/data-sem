import argparse
import logging

from logical_utils.tree import STree, is_tree_eq
from python_code_utils.scode import SCode, is_code_eq


def log(msg, print_stdout=True):
    if print_stdout:
        print(msg)
    logging.info(msg)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Evaluate accuracy of logical form.')
    parser.add_argument('--path',
                        default="../data/geo/8536_seq2seq_marking_10000step", )
    parser.add_argument('--type', required=False,
                        default="logic",
                        help="Choose type to run method compare in [logic|code]")
    parser.add_argument('--n_best', required=False, type=int,
                        default=1,
                        help="n best prediction by beam-search")
    args = parser.parse_args()
    print(args.path)

    logging.basicConfig(level=logging.DEBUG, filename="{}/result_logic.log".format(args.path), filemode="w+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
    method_eq = is_tree_eq
    obj_parser = STree
    if "django" in args.path or args.type == "code":
        method_eq = is_code_eq
        obj_parser = SCode

    data = {}
    for file_name in ["X_test_5.tsv", "Y_test_5.tsv", "Y_pred_5.tsv"]:
        with open("{}/{}".format(args.path, file_name), "rt", encoding="utf8") as f:
            lines = [l.strip() for l in f.readlines()]
            data[file_name] = lines
    count_all = len(data['X_test_5.tsv'])

    count_logic = 0
    count_exact_matching = 0
    count_nbest = 0
    for i, logic1 in enumerate(data["Y_test_5.tsv"]):
        for j in range(args.n_best):
            logic2 = data["Y_pred_5.tsv"][i * args.n_best + j]
            if j == 0:
                try:
                    if logic2 == logic1:
                        count_exact_matching += 1.0
                        break
                    elif method_eq(obj_parser(logic1), obj_parser(logic2), not_layout=True):
                        count_logic += 1.0
                        log("++ sentence {}, logic/code gold == logic/code pred ++".format(i))
                        log(logic1)
                        log(logic2)
                        break
                    else:
                        log("-- sentence {}, logic/code gold != logic/code pred --".format(i))
                        log(data["X_test_5.tsv"][i])
                        log(logic1)
                        log(logic2)
                except:
                    pass
            else:
                if (logic1 == logic2 or (
                        method_eq(obj_parser(logic1), obj_parser(logic2), not_layout=True))):
                    log("!! sentence {}, logic/code gold == logic/code pred {} !!".format(i, j + 1))
                    log(data["X_test_5.tsv"][i])
                    log(logic1)
                    log(logic2)
                    count_nbest += 1.0
                    break

    log(
        "exact match acc: {}, {}, {}".format(count_exact_matching, count_all, count_exact_matching / count_all))
    log(
        "logic/code acc : {}, {}, {}".format(count_logic, count_all, (count_exact_matching + count_logic) / count_all))
    log("logic/code using nbest = {}, {}, {}, {}".format(args.n_best, count_nbest, count_all,
                                                                  (count_exact_matching + count_nbest
                                                                   + count_logic) / count_all))
