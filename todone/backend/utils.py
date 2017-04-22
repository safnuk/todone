from todone import backend
import todone.parser.exceptions as pe


def match_folder(prefix):
    try:
        return backend.Folder.get_unique_match(prefix).name
    except backend.DatabaseError as e:
        if 'No match' in str(e):
            raise pe.ArgumentError(
                'No match found for folder {}/'.format(prefix))
        elif 'match' in str(e):
            raise pe.ArgumentError(
                'Multiple matches found for folder {}/'.format(prefix))
        else:
            raise e


def match_parent(**args):
    try:
        if not(args['folder'] or args['keywords']):
            return None
        if args['folder']:
            args['folder'] = match_folder(args['folder'])
        return backend.Todo.get_unique_match(**args)
    except backend.DatabaseError as e:
        folder_str = '{}/'.args['folder'] if args['folder'] else ''
        if 'No match' in str(e):
            raise pe.ArgumentError(
                'No match found for parent todo [{}]'
                .format(folder_str + ' '.join(args['keywords'])))
        elif 'match' in str(e):
            raise pe.ArgumentError(
                'Multiple matches found for parent todo [{}]'
                .format(folder_str + ' '.join(args['keywords'])))
        else:
            raise e
