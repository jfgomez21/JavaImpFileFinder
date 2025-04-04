command! -nargs=+ JIFF              call <SID>JavaImpFileFinder(<f-args>)

let s:pluginHome = expand("<sfile>:p:h:h")
let s:reloadScript = 0

if !s:reloadScript
	execute "py3file " . substitute(s:pluginHome, "\\", "/", "g") . "/pythonx/jiff.py"
endif

function! <SID>JavaImpFileFinder(...) 
	if has('python3')
		if s:reloadScript
			execute "py3file " . substitute(s:pluginHome, "\\", "/", "g") . "/pythonx/jiff.py"
		endif

		execute "python3 jiff_find_file()"
	else
		echom 'JavaImpFileFinder: No python support'
	endif
endfunction

function! JavaImpClassFinder(name) 
	if has('python3')
		if s:reloadScript
			execute "py3file " . substitute(s:pluginHome, "\\", "/", "g") . "/pythonx/jiff.py"
		endif

		execute "python3 jiff_find_java_class(\"" . a:name . "\")"
	else
		echom 'JavaImpFileFinder: No python support'
	endif
endfunction
