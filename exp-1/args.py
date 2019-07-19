import argparse

def get_exp1_train_test_args():
    parser = argparse.ArgumentParser("Arguments for exp1 training. Reminder to set the load_path for this to work.")
    _add_common_exp1_args(parser)
    parser.add_argument('--batch_size',
                        type=int,
                        default=32,
                        help='the size of each batch')
    parser.add_argument('--num_workers',
                        type=int,
                        default=8,
                        help='Number of subprocesses per data loader.')
    parser.add_argument("--dev_eval_file",
                        type=str,
                        default="data/dev/dev-eval.json", 
                        help="File reserved for storing dev evaluation data")
    parser.add_argument("--train_eval_file",
                        type=str,
                        default="data/test/test-eval.json", 
                        help="File reserved for storing test evaluation data")
    parser.add_argument('--num_visuals',
                        type=int,
                        default=10,
                        help='Number of examples to visualize in TensorBoard.')

    args = parser.parse_args()
    return args

def get_exp1_transform_args():
    parser = argparse.ArgumentParser("Arguments for transforming the raw data into exp1 format")
    _add_common_exp1_args(parser)
    args = parser.parse_args()
    return args

def get_data_gen_args():
    parser = argparse.ArgumentParser("Arguments for sub-sampling the raw data into smaller amounts to work w/ toy datasets")
    _add_common_exp1_args(parser)
    parser.add_argument("--train_topic_num",
                        type=int,
                        default=50,
                        help="The number of topics to put into the training_data_src")
    parser.add_argument("--dev_topic_num",
                        type=int,
                        default=20,
                        help="The number of topics to put into the dev_data_src")
    parser.add_argument("--test_topic_num",
                        type=int,
                        default=10,
                        help="The number of topics to put into the test_data_src")
    args = parser.parse_args()
    return args

def _add_common_exp1_args(parser):
    parser.add_argument("--raw_train_data",
                        type=str,
                        default="data/train/orig-train-v2.0.json", 
                        help="The entire corpus of raw training data")
    parser.add_argument("--raw_dev_data",
                        type=str,
                        default="data/dev/orig-dev-v2.0.json", 
                        help="The entire corpus of raw dev data")
    parser.add_argument("--raw_test_data",
                        type=str,
                        default="data/test/orig-test-v2.0.json", 
                        help="The entire corpus of raw test data")
    parser.add_argument("--train_data_src",
                        type=str,
                        default="data/train/train-v2.0.json", 
                        help="The subset of the raw data used as the training source")
    parser.add_argument("--dev_data_src",
                        type=str,
                        default="data/dev/dev-v2.0.json", 
                        help="The subset of the raw data used as the development sourcee")
    parser.add_argument("--test_data_src",
                        type=str,
                        default="data/test/test-v2.0.json", 
                        help="The subset of the raw data used as the  testing source")
    parser.add_argument("--train_data_exp1",
                        type=str,
                        default="data/train/train-exp1.json", 
                        help="The training data in exp1 format")
    parser.add_argument("--dev_data_exp1",
                        type=str,
                        default="data/dev/dev-exp1.json", 
                        help="The dev data in exp1 format")
    parser.add_argument("--test_data_exp1",
                        type=str,
                        default="data/test/test-exp1.json", 
                        help="The test data in exp1 format")
    parser.add_argument("--train_record_file_exp1",
                        type=str,
                        default="data/train/train-exp1.npz", 
                        help="File reserved storing the processed and prepped training data")
    parser.add_argument("--dev_record_file_exp1",
                        type=str,
                        default="data/dev/dev-exp1.npz", 
                        help="File reserved storing the processed and prepped dev data")
    parser.add_argument("--test_record_file_exp1",
                        type=str,
                        default="data/test/test-exp1.npz", 
                        help="File reserved storing the processed and prepped test data")
    parser.add_argument("--word_emb_file",
                        type=str,
                        default="data/embeddings/word-emb.json", 
                        help="File reserved for storing word embeddings")
    parser.add_argument("--logging_dir",
                        type=str,
                        default="./logs/",
                        help="The folder where all logs are stored")
    parser.add_argument("--save_dir",
                        type=str,
                        default="./save/",
                        help="The folder for storing general info")
    parser.add_argument("--load_path",
                        type=str,
                        default=None,
                        help="Load path where old good models are stored")
    parser.add_argument("--datasplit",
                        type=str,
                        default="all",
                        choices=("all", "train", "dev", "test"),
                        help="The number of topics in the original data put in the dev dataset")