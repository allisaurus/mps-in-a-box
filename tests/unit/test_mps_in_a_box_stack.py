import aws_cdk as core
import aws_cdk.assertions as assertions

from mps_in_a_box.mps_in_a_box_stack import MpsInABoxStack

# example tests. To run these tests, uncomment this file along with the example
# resource in mps_in_a_box/mps_in_a_box_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MpsInABoxStack(app, "mps-in-a-box")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
