from datasets import Audio
from datasets import load_dataset, DatasetDict, concatenate_datasets
from functools import partial


def prepare_dataset(batch, feature_extractor, tokenizer):
    # load and resample audio data from 48 to 16kHz
    audio = batch["audio"]

    # compute log-Mel input features from input audio array
    batch["input_features"] = feature_extractor(audio["array"], sampling_rate=audio["sampling_rate"]).input_features[0]

    # encode target text to label ids
    batch["labels"] = tokenizer(batch["transcription"]).input_ids
    return batch


def get_common_voice_dataset():
    common_voice = DatasetDict()

    common_voice["train"] = load_dataset("google/fleurs", "tg_tj", split="train+validation", )
    common_voice["test"] = load_dataset("google/fleurs", "tg_tj", split="test")

    common_voice = common_voice.remove_columns(
        ['id', 'num_samples', 'path', 'transcription', 'gender', 'lang_id', 'language', 'lang_group_id']
    )
    common_voice = common_voice.rename_column('raw_transcription', 'transcription')
    common_voice = common_voice.cast_column("audio", Audio(sampling_rate=16000))

    return common_voice


def get_assignment_dataset():
    assignment_dataset = load_dataset('audiofolder', data_dir='./dataset')
    assignment_dataset = assignment_dataset.cast_column("audio", Audio(sampling_rate=16000))

    return assignment_dataset


def prep_asr_datasets(feature_extractor, tokenizer):
    common_voice_dataset = get_common_voice_dataset()
    assignment_dataset = get_assignment_dataset()

    main_dataset = DatasetDict()
    main_dataset['train'] = concatenate_datasets([common_voice_dataset['train'],
                                                  assignment_dataset['train']])

    main_dataset['test'] = concatenate_datasets([common_voice_dataset['test'],
                                                 assignment_dataset['test']])

    main_dataset = main_dataset.map(
        partial(prepare_dataset, feature_extractor=feature_extractor, tokenizer=tokenizer),
        remove_columns=main_dataset.column_names["train"],
        num_proc=2
    )
    return main_dataset


def prep_asr_test_dataset(feature_extractor, tokenizer):
    assignment_dataset = get_assignment_dataset()

    test_dataset = DatasetDict()
    test_dataset['test'] = assignment_dataset['test']

    test_dataset = test_dataset.map(
        partial(prepare_dataset, feature_extractor=feature_extractor, tokenizer=tokenizer),
        remove_columns=test_dataset.column_names['test'],
        num_proc=2
    )
    return test_dataset


def main():
    pass


if __name__ == '__main__':
    main()