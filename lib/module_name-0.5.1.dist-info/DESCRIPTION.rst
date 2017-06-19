module_name
===========

Simple module to make it easy to run python files with `-m` flag.

The benefits of running with `-m` is that your relative imports will work.
Running a python file as a script doesn't understand that it is part of a
package.

```
usage: py-module-name [-h] [-f] [-d] path

positional arguments:
  path         path to python file

optional arguments:
  -h, --help   show this help message and exit
  -f, --flag   Will output -m flag if path is importable
  -d, --debug  Debug
```

## Examples

```
> py-module-name module_name/resolve.py
module_name.resolve

> py-module-name -f module_name/resolve.py
-m 'module_name.resolve'

> py-module-name -f /tmp/not_package/standalone.py
'/tmp/not_package/standalone.py'
```

The `-f` flag is useful for use with scripting. I use it from my `.vimrc` to
run files I am editing.

## .vimrc
```
autocmd FileType python map <buffer> <S-r> :w<CR>:!tmux send-keys -t :.{bottom-right} "\%time \%run `py-module-name -f %:p`" enter<CR><CR>
```


