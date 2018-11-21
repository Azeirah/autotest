import PHPTraceTokenizer
import PHPProfileParser
import PHPTraceParser
import os


traceDir = "test-data"

def trace_and_profile_from_timestamp(traceDir, timestamp):
    return (
        os.path.join(traceDir, "{}.xt".format(timestamp)),
        os.path.join(traceDir, "{}.xp".format(timestamp))
    )

def create_trace(traceFile, profileFile):
    function_mappings = PHPProfileParser.get_function_file_mapping(profileFile)
    return PHPTraceTokenizer.Trace(traceFile, function_mappings)


def traceNoExceptionsTest(timestamp):
    traceFile, profileFile = trace_and_profile_from_timestamp(traceDir, timestamp)
    trace = create_trace(traceFile, profileFile)


traceNoExceptionsTest('1541770537')