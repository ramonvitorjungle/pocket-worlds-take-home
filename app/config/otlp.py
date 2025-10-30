from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def telemetry(app: FastAPI):
    trace_provider = TracerProvider()
    otlp_exporter = OTLPSpanExporter(endpoint="your-otlp-endpoint")
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(trace_provider)
    FastAPIInstrumentor.instrument_app(app)
