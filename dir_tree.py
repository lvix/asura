import os


tree = ['asura', 
        ['dbconnector'], 
        ['exceptions'], 
        ['helper'], 
        ['route'], 
        ['session'], 
        ['template_engine'], 
        ['view'], 
        ['wsgi_adapter'],
        ]

def create_tree(path_prefix, tree):
    dir_name = tree[0]
    # create_self
    if os.path.exists(path_prefix + dir_name):
        print('directory <{}> already exists'.format(dir_name))
    else:
        try:
            os.mkdir(path_prefix + dir_name)
            print('created directory <{}>'.format(dir_name))
        except Exception as e:
            print('creating directory <{}> failed'.format(dir_name))
            print(e)
    
    # create __init__.py
    init_file_path = path_prefix + dir_name + '/__init__.py'
    if not os.path.isfile(init_file_path):
        try:
            with open(init_file_path, 'w') as f:
                print('created __init__.py for <{}>'.format(dir_name))
        except Exception as e:
            print('creating file __init__.py failed')
            print(e)

    # create sub directories 
    for i in range(1, len(tree)):
        create_tree(path_prefix + dir_name + '/', tree[i])
    
def main():
    dir_prefix = os.getcwd() + '/'
    create_tree(dir_prefix, tree)

if __name__ == '__main__':
    main()

    



