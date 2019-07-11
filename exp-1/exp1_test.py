"""Test a model and generate submission CSV.

Usage:
    > python test.py --split SPLIT --load_path PATH --name NAME
    where
    > SPLIT is either "dev" or "test"
    > PATH is a path to a checkpoint (e.g., save/train/model-01/best.pth.tar)
    > NAME is a name to identify the test run

Author:
    Chris Chute (chute@stanford.edu)
"""

import csv
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data as data
import util

import config
from collections import OrderedDict
from json import dumps
from models import BiDAF
from os.path import join
from tensorboardX import SummaryWriter
from tqdm import tqdm
from ujson import load as json_load
from util import collate_fn, SQuAD
from toolkit import get_logger


def main(c, flags):
    # Set up logging
    data_split = flags[1]
    if data_split == "train":
        eval_file = c.train_eval_file
        record_file = c.train_record_file_exp1
    if data_split == "toy":
        eval_file = c.toy_eval_file
        record_file = c.toy_record_file_exp1
    else:
        eval_file = None
        record_file = None
        raise ValueError("Unregonized or missing flag")

    c.save_dir = util.get_save_dir(c.save_dir, "results", training=False)
    log = get_logger(c.save_dir, "results")
    log.info(f'Args: {dumps(vars(c), indent=4, sort_keys=True)}')
    device, gpu_ids = util.get_available_devices()
    c.batch_size *= max(1, len(gpu_ids))

    # Get embeddings
    log.info('Loading embeddings...')
    word_vectors = util.torch_from_json(c.word_emb_file)

    # Get model
    log.info('Building model...')
    model = BiDAF(word_vectors=word_vectors,
                  hidden_size=c.hidden_size)
    model = nn.DataParallel(model, gpu_ids)
    log.info(f'Loading checkpoint from {c.load_path}...')
    model = util.load_model(model, c.save_dir, gpu_ids, return_step=False)
    model = model.to(device)
    model.eval()

    # Get data loader
    log.info('Building dataset...')
    dataset = SQuAD(record_file, True)
    data_loader = data.DataLoader(dataset,
                                  batch_size=c.batch_size,
                                  shuffle=False,
                                  num_workers=c.num_workers,
                                  collate_fn=collate_fn)

    # Evaluate
    log.info(f'Evaluating on {data_split} split...')
    nll_meter = util.AverageMeter()
    pred_dict = {}  # Predictions for TensorBoard
    sub_dict = {}   # Predictions for submission
    with open(eval_file, 'r') as fh:
        gold_dict = json_load(fh)
    with torch.no_grad(), \
            tqdm(total=len(dataset)) as progress_bar:
        for cw_idxs, cc_idxs, qw_idxs, qc_idxs, y1, y2, ids in data_loader:
            # Setup for forward
            cw_idxs = cw_idxs.to(device)
            qw_idxs = qw_idxs.to(device)
            batch_size = cw_idxs.size(0)

            # Forward
            log_p1, log_p2 = model(cw_idxs, qw_idxs)
            y1, y2 = y1.to(device), y2.to(device)
            loss = F.nll_loss(log_p1, y1) + F.nll_loss(log_p2, y2)
            nll_meter.update(loss.item(), batch_size)

            # Get F1 and EM scores
            p1, p2 = log_p1.exp(), log_p2.exp()
            starts, ends = util.discretize(p1, p2, c.max_ans_len, True)

            # Log info
            progress_bar.update(batch_size)

            # Not using the unlabeled test set
#            if args.split != 'test':
#                # No labels for the test set, so NLL would be invalid
#                progress_bar.set_postfix(NLL=nll_meter.avg)

            idx2pred, uuid2pred = util.convert_tokens(gold_dict,
                                                      ids.tolist(),
                                                      starts.tolist(),
                                                      ends.tolist(),
                                                      True)
            pred_dict.update(idx2pred)
            sub_dict.update(uuid2pred)

    # Log results (except for test set, since it does not come with labels)
    results = util.eval_dicts(gold_dict, pred_dict, True)
    results_list = [('NLL', nll_meter.avg),
                    ('F1', results['F1']),
                    ('EM', results['EM'])]
    if args.use_squad_v2:
        results_list.append(('AvNA', results['AvNA']))
    results = OrderedDict(results_list)
    # Log to console
    results_str = ', '.join(f'{k}: {v:05.2f}' for k, v in results.items())
    log.info(f'{data_split} {results_str}')
    # Log to TensorBoard
    tbx = SummaryWriter(c.save_dir)
    util.visualize(tbx,
                   pred_dict=pred_dict,
                   eval_path=eval_file,
                   step=0,
                   split="Dev",
                   num_visuals=c.num_visuals)
 # Write submission file
    # I'm not focused on the submission file
#    sub_path = join(args.save_dir, args.split + '_' + args.sub_file)
#    log.info(f'Writing submission file to {sub_path}...')
#    with open(sub_path, 'w', newline='', encoding='utf-8') as csv_fh:
#        csv_writer = csv.writer(csv_fh, delimiter=',')
#        csv_writer.writerow(['Id', 'Predicted'])
#        for uuid in sorted(sub_dict):
#            csv_writer.writerow([uuid, sub_dict[uuid]])


if __name__ == '__main__':
    c = config.config()
    flags = sys.argv
    main(c, flags)
