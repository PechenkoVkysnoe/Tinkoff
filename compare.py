import ast
import codecs
import argparse


class DeleteAnnotation(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        node.returns = None
        if node.args.args:
            for arg in node.args.args:
                arg.annotation = None
        return node


def delete_docstring(tree):
    for node in ast.walk(tree):
        try:
            if not len(node.body):
                continue
        except:
            continue

        if not isinstance(node.body[0], ast.Expr):
            continue

        if not hasattr(node.body[0], 'value') or not isinstance(node.body[0].value, ast.Str):
            continue

        node.body = node.body[1:]


def file_preparation(name):
    with codecs.open(name, 'r', "utf_8_sig") as file:
        ast_tree = ast.parse(file.read())
        transform = DeleteAnnotation().visit(ast_tree)
        delete_docstring(transform)
        result_file = ast.unparse(transform)

    return result_file
    # with codecs.open(name, 'w', "utf_8_sig") as file:
    #     file.write(result_file)


def string_ordering(first, second):
    if len(first) <= len(second):
        return first, second
    else:
        return second, first


def levenshtein(first, second):
    def m(a, b):
        if a == b:
            return 0
        else:
            return 1

    first, second = string_ordering(first, second)
    current_line = [i for i in range(len(first) + 1)]

    for i in range(1, len(second) + 1):
        current_line, previous_line = [0 for _ in range(len(first) + 1)], current_line
        current_line[0] = i
        for j in range(1, len(first) + 1):
            current_line[j] = min(current_line[j - 1] + 1, previous_line[j] + 1,
                                  previous_line[j - 1] + m(first[j - 1], second[i - 1]))

    return current_line[-1]


parser = argparse.ArgumentParser(description='Calculate plagiarism scores')
parser.add_argument('input', type=str, help='1')
parser.add_argument('output', type=str, help='2')
args = parser.parse_args()

if __name__ == '__main__':
    with open(args.input, 'r') as input_file:
        result_scores = []
        for line in input_file:
            first_path, second_path = line.split()
            first_file = file_preparation(first_path)
            second_file = file_preparation(second_path)
            result_scores.append(1 - (levenshtein(first_file, second_file) * 2) / (len(first_file) + len(second_file)))

    with open(args.output, 'w') as output_file:
        for score in result_scores:
            output_file.write(str(score))
