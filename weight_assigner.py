import collections
import igraph as ig


class WeightAssigner:
    '''
    Given a labelled graph, this class assigns weights based on
    a similarity measure and an assignment strategy and returns
    the weighted graph.
    '''

    def __init__(self, ignore_label_order=False, similarity='hamming'):
        self._ignore_label_order = ignore_label_order
        self._similarity = None

        # Select similarity measure to use in the `fit_transform()`
        # function later on.
        if similarity == 'hamming':
            self._similarity = self._hamming
        elif similarity == 'jaccard':
            self._similarity = self._jaccard

        if not self._similarity:
            raise RuntimeError('Unknown similarity measure \"{}\" requested'.format(similarity))

    def fit_transform(self, graph):

        for edge in graph.es:
            source, target = edge.tuple

            source_labels = graph.vs[source]['label']
            target_labels = graph.vs[target]['label']

            # FIXME: this does not yet take the original label of the
            # node into account. For this, I would need to split this
            # array or use the first entry.
            weight = self._similarity(source_labels, target_labels)
            weight = 1.0 - weight

            edge['weight'] = weight

        return graph

    def _hamming(self, A, B):
        '''
        Computes the (normalized) Hamming distance between two sets of
        labels A and B. This amounts to counting how many overlaps are
        present in the sequences.
        '''

        n = len(A) + len(B)

        counter = collections.Counter(A)
        counter.subtract(B)

        num_missing = sum([abs(c) for _, c in counter.most_common()])
        return num_missing / n

    def _jaccard(A, B):
        '''
        Computes the Jaccard index between two sets of labels A and B. The
        measure is in the range of [0,1], where 0 indicates no overlap and
        1 indicates a perfect overlap.
        '''

        A = set(A)
        B = set(B)

        return len(A.intersection(B)) / len(A.union(B))


# FIXME: remove after debug
if __name__ == '__main__':
    graph = ig.read('data/MUTAG/000.gml')
    print('Before:', graph.es['weight'])
    WeightAssigner().fit_transform(graph)
    print('After:', graph.es['weight'])