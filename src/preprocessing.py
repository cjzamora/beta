# -*- coding: utf-8 -*-

class Processor():
    # prepare data the same with training
    # data structure
    def prepare(self, object):
        # prepared object
        prepared = {
            'labels'    : [],
            'features'  : []
        }

        # iterate on each object
        for i in object:
            # append label
            prepared['labels'].append(i['label'])

            # get computed styles
            computed = i['computed']

            # set tag path
            computed['tag_path'] = ' > '.join(i['path'])    

            # append features
            prepared['features'].append(computed)

        return prepared