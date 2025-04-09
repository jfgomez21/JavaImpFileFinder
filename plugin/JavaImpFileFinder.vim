command! -nargs=+ JIFF              call <SID>JavaImpFileFinder(<f-args>)

let s:pluginHome = expand("<sfile>:p:h:h")
let s:loadScript = 1

function! <SID>JavaImpFileFinder(...) 
	if has('python3')
		if s:loadScript
			execute "py3file " . substitute(s:pluginHome, "\\", "/", "g") . "/pythonx/jiff.py"

			let s:loadScript = 0
		endif

		execute "python3 jiff_find_file()"
	else
		echom 'JavaImpFileFinder: No python support'
	endif
endfunction

function! JavaImpClassFinder(name) 
	if has('python3')
		if s:loadScript
			execute "py3file " . substitute(s:pluginHome, "\\", "/", "g") . "/pythonx/jiff.py"
			
			let s:loadScript = 0
		endif

		execute "python3 jiff_find_java_class(\"" . a:name . "\")"
	else
		echom 'JavaImpFileFinder: No python support'
	endif
endfunction
