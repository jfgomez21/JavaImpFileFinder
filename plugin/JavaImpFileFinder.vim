command! -nargs=+ JIFF              call <SID>JavaImpFileFinder(<f-args>)
command! -nargs=+ FF              call <SID>JavaImpRegularFileFinder(<f-args>)
command! -nargs=+ FFI              call <SID>JavaImpRegularFileFinderInsert(<f-args>)

let s:pluginHome = expand("<sfile>:p:h:h")
let s:loadScript = 1

if !exists("g:JavaImpFileFinderExcludeDirs")
    let g:JavaImpFileFinderExcludeDirs = "target"
endif

function! <SID>JavaImpFileFinder(...) 
	if has('python3')
		if s:loadScript
			execute "py3file " . substitute(s:pluginHome, "\\", "/", "g") . "/pythonx/jiff.py"

			let s:loadScript = 0
		endif

		execute "python3 jiff_find_java_file()"
	else
		echom 'JavaImpFileFinder: No python support'
	endif
endfunction

function! <SID>JavaImpRegularFileFinder(...) 
	if has('python3')
		if s:loadScript
			execute "py3file " . substitute(s:pluginHome, "\\", "/", "g") . "/pythonx/jiff.py"

			let s:loadScript = 0
		endif

		execute "python3 jiff_find_regular_file()"
	else
		echom 'JavaImpFileFinder: No python support'
	endif
endfunction

function! <SID>JavaImpRegularFileFinderInsert(...) 
	if has('python3')
		if s:loadScript
			execute "py3file " . substitute(s:pluginHome, "\\", "/", "g") . "/pythonx/jiff.py"

			let s:loadScript = 0
		endif

		execute "python3 jiff_find_regular_file_insert()"
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
