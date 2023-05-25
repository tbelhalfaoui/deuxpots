from dataclasses import asdict
from flask import Flask
from flask import Flask, request
from flask_cors import CORS
from prometheus_client import Histogram, Counter
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics

from deuxpots.demo import DEMO_FLAT_BOXES
from deuxpots import CERFA_VARIABLES_PATH, CATEGORY_COORDS_PATH, DEV_MODE
from deuxpots.box import load_box_mapping
from deuxpots.flatbox import FlatBox, flatten
from deuxpots.individualize import simulate_and_individualize
from deuxpots.pdf_tax_parser import load_category_coords, parse_tax_pdf
from deuxpots.valued_box import ValuedBox
from deuxpots.warning_error_utils import DEFAULT_USER_ERROR_MESSAGE, UserFacingError, UserFacingWarning, handle_warnings

BOX_MAPPING = load_box_mapping(CERFA_VARIABLES_PATH)
FAMILY_BOX_COORDS = load_category_coords(CATEGORY_COORDS_PATH)

PROM_REQUEST_TIME = Histogram('parse_processing_seconds', 'Response time of the route.', ['route'])
PROM_ERROR_COUNT = Counter('error_count', 'Count the HTTP errors returned.', ['route', 'code', 'error', 'arg'])


app = Flask("deuxpots")
app.config['PROPAGATE_EXCEPTIONS'] = False
if DEV_MODE:
    CORS(app)

metrics_app = GunicornPrometheusMetrics(app)


@app.errorhandler(UserFacingError)
def handle_bad_request(e):
    app.logger.error(f"{type(e).__name__}: {e.args[0]}")
    PROM_ERROR_COUNT.labels(request.path, 400, type(e).__name__, e.args[0]).inc()
    return str(e), 400


@app.errorhandler(Exception)
def handle_bad_request(e):
    app.logger.exception("EXCEPTION")
    PROM_ERROR_COUNT.labels(request.path, 500, type(e).__name__, e.args[0]).inc()
    return DEFAULT_USER_ERROR_MESSAGE, 500


@PROM_REQUEST_TIME.labels('/parse').time()
@app.route('/parse', methods=['POST'])
@handle_warnings(UserFacingWarning)
def parse():
    if request.args.get('demo'):
        return dict(
            boxes=[asdict(flatten(ValuedBox.from_flat_box(flatbox, BOX_MAPPING))) for flatbox in DEMO_FLAT_BOXES]
        )
    tax_pdf = request.files['tax_pdf'].read()
    valboxes = parse_tax_pdf(tax_pdf, FAMILY_BOX_COORDS, BOX_MAPPING)
    return dict(
        boxes=[asdict(flatten(valbox)) for valbox in valboxes]
    )


@PROM_REQUEST_TIME.labels('/individualize').time()
@app.route('/individualize', methods=['POST'])
def individualize():
    user_boxes = [FlatBox(code=box['code'],
                          raw_value=box['raw_value'],
                          attribution=box['attribution'])
                  for box in request.json['boxes']]
    valboxes = [ValuedBox.from_flat_box(flatbox, BOX_MAPPING)
                for flatbox in user_boxes]
    result = simulate_and_individualize(valboxes)
    return dict(
        individualized=asdict(result)
    )
