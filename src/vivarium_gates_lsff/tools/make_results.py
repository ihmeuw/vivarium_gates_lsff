from pathlib import Path
import shutil

from loguru import logger

from vivarium_gates_lsff.results_processing import process_results
from vivarium_gates_lsff.constants.results import TEMPLATE_FIELD_MAP


def build_results(output_file: str, single_run: bool):
    output_file = Path(output_file)
    measure_dir = output_file.parent / 'count_data'
    if measure_dir.exists():
        shutil.rmtree(measure_dir)
    measure_dir.mkdir(exist_ok=True, mode=0o775)

    logger.info(f'Reading in output data from {str(output_file)}.')
    data, keyspace, years = process_results.read_data(output_file, single_run)

    # Get the actual number of years the sim ran. It is sometimes helpful
    #  to run for less than the full duration and that will cause an error
    #  when using the default time period
    field_map = TEMPLATE_FIELD_MAP.copy()
    field_map['YEAR'] = tuple(range(years[0], years[1]))

    logger.info(f'Filtering incomplete data from outputs.')
    rows = len(data)
    data = process_results.filter_out_incomplete(data, keyspace)
    new_rows = len(data)
    logger.info(f'Filtered {rows - new_rows} from data due to incomplete information.  {new_rows} remaining.')
    data = process_results.aggregate_over_seed(data, field_map)
    logger.info(f'Computing raw count and proportion data.')
    measure_data = process_results.make_measure_data(data, field_map)
    logger.info(f'Writing raw count and proportion data to {str(measure_dir)}')
    measure_data.dump(measure_dir)
    logger.info('**DONE**')
