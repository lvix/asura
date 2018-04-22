import os 
import re 

# a Jinja2 mark 
pattern = r'{{(.*?)}}'

# parse 
def parse_args(obj):
    comp = re.compile(pattern)

    ret = comp.findall(obj)

    return ret if ret else ()

# return template content 
def replace_template(app, path, **options):

    content = '<h1>Template Not Found</h1>'

    path = os.path.join(app.template_folder, path)


    if os.path.exists(path):

        with open(path, 'rb') as f:
            content = f.read().decode()

        args = parse_args(content)

        if options:
            for arg in args:
                key = arg.strip()

                content = content.replace('{{{{{}}}}}'.format(arg), str(options.get(key, '')))
        return content 

