from pathlib import Path

from k2db.utils import ConfigHandler
from k2db.mapper import Mapper
from k2db.evaluation import EvaluationHandler


approaches = ['standard','pospruning','prepruning']
# approaches = ['pospruning','prepruning']

config = ConfigHandler()
queryset_configs = config.get_queryset_configs()
queryset_configs.sort()

instance_based_approaches_parallel_cn = False
output_results_subfolder = 'assume_golden_qms/'

spark_context = None

repeat = 1 
parallel_cn = False
assume_golden_qms=True
topk_cns_per_qm = 20
input_desired_cn=True

for weight_scheme in range(4):
    output_results_subfolder = f'assume_golden_qms/ws{weight_scheme}/'
    Path(f'{config.results_directory}{output_results_subfolder}').mkdir(parents=True, exist_ok=True)

    for approach in approaches:
        
        prepruning = (approach == 'prepruning')
        pospruning = (approach == 'pospruning')
        # if approach == 'standard':
        #     repeat = 10
        #     parallel_cn = False        
        # else:
        #     repeat = 1 
        #     parallel_cn = instance_based_approaches_parallel_cn

        for qsconfig_name,qsconfig_filepath in queryset_configs:

            config = ConfigHandler(reset = True,queryset_config_filepath=qsconfig_filepath)
            mapper = Mapper()
            evaluation_handler = EvaluationHandler()
            mapper.load_queryset()

            if parallel_cn:
                mapper.load_spark(spark_context = spark_context,num_workers=2)
                spark_context = mapper.spark_context

            evaluation_handler.load_golden_standards()

            print(f'Running queryset {config.queryset_name} with {approach} approach')

            results_filepath = f'{config.results_directory}{output_results_subfolder}{config.queryset_name}-{approach}.json'

            results = mapper.run_queryset(
                parallel_cn= parallel_cn,
                repeat = repeat,
                prepruning=prepruning,
                pospruning=pospruning,
                weight_scheme=weight_scheme,
                assume_golden_qms = assume_golden_qms,
                topk_cns_per_qm = topk_cns_per_qm,
                input_desired_cn = input_desired_cn,
                )
            
            print(f'Saving results in {results_filepath}')
            evaluation_handler.evaluate_results(results,results_filename=results_filepath)