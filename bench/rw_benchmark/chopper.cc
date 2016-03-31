#include "all.h"

namespace deptran {

void RWChopper::W_txn_init(TxnRequest &req) {
  inputs_.clear();
  inputs_[RW_BENCHMARK_W_TXN_0] = map<int32_t, Value>({{0, req.input_[0]}});
  n_pieces_input_ready_ = 1;

  output_size_ = {{0,0}};
  p_types_ = {{RW_BENCHMARK_W_TXN_0, RW_BENCHMARK_W_TXN_0}};
  sss_->GetPartition(RW_BENCHMARK_TABLE, req.input_[0], sharding_[RW_BENCHMARK_W_TXN_0]);
  status_ = {{RW_BENCHMARK_W_TXN_0, READY}};
  n_pieces_all_ = 1;
}

void RWChopper::R_txn_init(TxnRequest &req) {
  inputs_.clear();
  inputs_[RW_BENCHMARK_R_TXN_0] = map<int32_t, Value>({{0, req.input_[0]}});
  n_pieces_input_ready_ = 1;

  output_size_= {{0, 1}};
  p_types_ = {{RW_BENCHMARK_R_TXN_0, RW_BENCHMARK_R_TXN_0}};
  sss_->GetPartition(RW_BENCHMARK_TABLE, req.input_[0], sharding_[RW_BENCHMARK_R_TXN_0]);
  status_ = {{RW_BENCHMARK_R_TXN_0, READY}};
  n_pieces_all_ = 1;
}

RWChopper::RWChopper() {
}

void RWChopper::init(TxnRequest &req) {
  type_ = req.txn_type_;
  callback_ = req.callback_;
  max_try_ = req.n_try_;
  n_try_ = 1;
  commit_.store(true);
  switch (req.txn_type_) {
    case RW_BENCHMARK_W_TXN:
      W_txn_init(req);
      break;
    case RW_BENCHMARK_R_TXN:
      R_txn_init(req);
      break;
    default:
      verify(0);
  }
}

bool RWChopper::start_callback(const std::vector<int> &pi,
                               int res, BatchStartArgsHelper &bsah) {
  return false;
}

bool RWChopper::start_callback(int pi,
                               int res,
                               map<int32_t, Value> &output) {
  return false;
}

bool RWChopper::is_read_only() {
  if (type_ == RW_BENCHMARK_W_TXN)
    return false;
  else if (type_ == RW_BENCHMARK_R_TXN)
    return true;
  else
    verify(0);
}

void RWChopper::Reset() {
  TxnChopper::Reset();
  for (auto& pair : status_) {
    pair.second = READY;
  }
  commit_.store(true);
  partition_ids_.clear();
  n_pieces_input_ready_ = 1;
  n_try_++;
}

RWChopper::~RWChopper() {
}

}
