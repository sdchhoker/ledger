import json

from ledger.immutable_store.error import GeneralMissingError
from ledger.immutable_store.merkle import TreeHasher
from ledger.immutable_store.merkle_tree import MerkleTree
from ledger.immutable_store.store import ImmutableStore, F


class Ledger:

    def __init__(self, tree: MerkleTree, store: ImmutableStore):
        """
        :param tree: an implementation of MerkleTree used to store events
        """
        # TODO The initialization logic should take care of migrating the
        # persisted data into a newly created Merkle Tree after server restart.
        self.tree = tree
        self.store = store
        self.hasher = TreeHasher()
        self.serialNo = store.lastCount()
        self.recoverTree()

    def recoverTree(self):
        for key, entry in self.store.getAll():
            record = eval(entry.decode('utf-8'))
            self._addToTree(record)

    def add(self, data):
        data['serial_no'] = (self.serialNo + 1)
        self.serialNo += 1
        self._addToTree(data)
        self._addToStore(data)

    def _addToTree(self, data):
        leaf_data_hash = data[F.leaf_data_hash.name]
        leaf_data = data[F.leaf_data.name]
        if leaf_data_hash:
            self.tree.append(leaf_data_hash)
        elif leaf_data:
            leaf_hash = self.hasher.hash_leaf(bytes(str(leaf_data), 'utf-8'))
            self.tree.append(leaf_hash)
            leaf_data_hash = leaf_hash
        else:
            raise GeneralMissingError("Transaction not found.")

    def _addToStore(self, data):
        key = data['serial_no']
        self.store.append(key, data)

