from utils import scrape_dependents
from datasets import Dataset, DatasetDict

repository = "transformers"
owner = "huggingface"

dataset_dict = DatasetDict()

for dependent_type in ['package', 'repository']:
    with open(f'{dependent_type}.txt', 'w+') as f:
        results = scrape_dependents(owner, repository, dependent_type=dependent_type)

        dictionary = {
            'name': [],
            'stars': [],
            'forks': []
        }

        for i, result in enumerate(results):
            dictionary['name'].append(result['name'])
            dictionary['stars'].append(result['stars'])
            dictionary['forks'].append(result['forks'])

            f.write(str(result) + '\n')

        dataset = Dataset.from_dict(dictionary)
        dataset.save_to_disk(f'./{dependent_type}.ds')
        dataset_dict[dependent_type] = dataset

dataset_dict.push_to_hub(f'open-source-metrics/{repository}-dependents')
