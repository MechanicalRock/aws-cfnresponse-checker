import json        

class Reporter:
    def _pretty_list(self, list):
        return ('\n').join(map(lambda item: "- " + item, list))

    def _length_of_longest_names(self, function_report):
        max_stack_name_length, max_function_name_length, max_code_name_length = 0, 0, 0
        for stack in function_report:
            max_stack_name_length = max(len(stack["stack"]), max_stack_name_length)
            for function in stack["functions"]:
                max_function_name_length = max(len(function["logicalId"]), max_function_name_length)
                max_code_name_length = max(len(function["code"]), max_code_name_length)

        return [max_stack_name_length, max_function_name_length, max_code_name_length]

    def _pretty_function(self, stack, length_of_longest_names):
        stack_width, function_width, code_width = length_of_longest_names
        return ('\n').join(map(lambda function: f'| {stack["stack"]: <{stack_width}} | {function["logicalId"]: <{function_width}} | {function["code"]: <{code_width}} |', stack["functions"]))
        

    def _pretty_function_report(self, function_report):
        length_of_longest_names = self._length_of_longest_names(function_report)
        stack_width, function_width, code_width = length_of_longest_names
        headers = f'| {"Stack": <{stack_width}} | {"Function": <{function_width}} | {"Code": <{code_width}} |'
        table_data = ('\n').join(map(lambda stack: self._pretty_function(stack, length_of_longest_names), function_report))
        
        return headers + '\n' + table_data+'\n'   

    def pretty_problem_report(self, problem_report):
        return f'''The following stacks are out of date and need to be re-deployed:
To fix add a comment to the inline code in your CloudFormation template.
{self._pretty_list(problem_report["stacks"])}

The following stacks contain the use of deprecated `botocore.vendored` and MUST be updated:
To fix update the Runtime Property for the function in your CloudFormation template to Python 3.8
{self._pretty_list(problem_report["inline_vendored_usage"])}

The following stacks contain Python functions.  These could not be evaluated, but should be reviewed for deprecated usage:
{self._pretty_function_report(problem_report["function_report"])}'''
