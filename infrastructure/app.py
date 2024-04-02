import aws_cdk as cdk
from stacks.chaliceapp import ChaliceApp

app = cdk.App()
ChaliceApp(app, 'transcriber')

app.synth()
