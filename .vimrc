"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" => General
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Sets how many lines of history VIM has to remember
set history=700

execute pathogen#infect()

"autocmd vimenter * NERDTree

"autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 0 && !exists("s:std_in") | NERDTree | endif
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTreeType") && b:NERDTreeType == "primary") | q | endif
autocmd VimEnter * wincmd p
map <C-n> :NERDTreeToggle<CR>
let NERDTreeShowHidden=1

" Enable filetype plugins
filetype plugin on
filetype indent on

" Set to auto read when a file is changed from the outside
set autoread

" With a map leader it's possible to do extra key combinations
" like <leader>w saves the current file
let mapleader = ","
let g:mapleader = ","

" Fast saving
nmap <leader>w :w!<cr>

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" => VIM user interface
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Set 7 lines to the cursor - when moving vertically using j/k
set so=7

" Turn on the WiLd menu
set wildmenu

" Ignore compiled files
set wildignore=*.o,*~,*.pyc

" A buffer becomes hidden when it is abandoned
set hid


" No annoying sound on errors
set noerrorbells
set visualbell
set t_vb=
set tm=500

set cursorline
set encoding=utf-8
set modelines=0
set autoindent
set showmode
set showcmd
set hidden
set visualbell
set ttyfast
set ruler
set backspace=indent,eol,start
set number
set norelativenumber
set laststatus=2
set history=1000
set undofile
set undoreload=10000
" set list
set lazyredraw
set matchtime=3
" set showbreak=â†ª
set splitbelow
set splitright
set autowrite
set autoread
set shiftround
set title
set linebreak
set nobackup
" set colorcolumn=+1
"set guifont=Terminus\ 10
" set nobackup
nnoremap gw "_yiw:s/\(\%#\w\+\)\(\_W\+\)\(\w\+\)/\3\2\1/<CR><C-o><C-l>

vmap <C-c> "+y
nmap <C-v> "+gP
"imap <C-v> "+gP
nmap <C-a> ggVG
vmap <C-x> "+x
set pastetoggle=<F10>
inoremap <C-v> <F10><C-r>+<F10>
set clipboard=unnamedplus

let g:indent_guides_enable_on_vim_startup = 0
let g:indent_guides_auto_colors = 0
autocmd VimEnter,Colorscheme * :hi IndentGuidesOdd  guibg=black   ctermbg=232
autocmd VimEnter,Colorscheme * :hi IndentGuidesEven guibg=black ctermbg=233

set foldmethod=indent
" Colors and Fonts--------------------------------------------------------- {{{
" Enable syntax highlighting
syntax enable

"colorscheme elflord
"set background=dark

" Set extra options when running in GUI mode
if has("gui_running")
    set guioptions-=T
    set guioptions+=e
    set t_Co=256
    set guitablabel=%M\ %t
endif

" Use Unix as the standard file type
set ffs=unix,dos,mac

set background=dark

hi clear

if exists("syntax_on")
  syntax reset
endif

" Set environment to 256 colours
set t_Co=256

let colors_name = "marussian"

if version >= 700
  hi CursorLine     guibg=#000208 ctermbg=16
  hi CursorColumn   guibg=#000208 ctermbg=16
  hi MatchParen     guifg=#FF007B guibg=#000208 gui=bold ctermfg=198 ctermbg=16 cterm=bold
  hi Pmenu          guifg=#FFFFFF guibg=#323232 ctermfg=255 ctermbg=236
  hi PmenuSel       guifg=#FFFFFF guibg=#F99085 ctermfg=255 ctermbg=210
endif

" Background and menu colors
hi Cursor           guifg=NONE guibg=#FFFFFF ctermbg=255 gui=none
hi Normal           guifg=#FFFFFF guibg=#000208 gui=none ctermfg=255 ctermbg=16 cterm=none
hi NonText          guifg=#FFFFFF guibg=#0F1117 gui=none ctermfg=255 ctermbg=233 cterm=none
hi LineNr           guifg=#FFFFFF guibg=#191B21 gui=none ctermfg=255 ctermbg=234 cterm=none
hi StatusLine       guifg=#FFFFFF guibg=#311E21 gui=italic ctermfg=255 ctermbg=235 cterm=italic
hi StatusLineNC     guifg=#FFFFFF guibg=#282A30 gui=none ctermfg=255 ctermbg=236 cterm=none
hi VertSplit        guifg=#FFFFFF guibg=#191B21 gui=none ctermfg=255 ctermbg=234 cterm=none
hi Folded           guifg=#FFFFFF guibg=#000208 gui=none ctermfg=255 ctermbg=16 cterm=none
hi Title            guifg=#F99085 guibg=NONE	gui=bold ctermfg=210 ctermbg=NONE cterm=bold
hi Visual           guifg=#9C8EE4 guibg=#323232 gui=none ctermfg=140 ctermbg=236 cterm=none
hi SpecialKey       guifg=#C14AFF guibg=#0F1117 gui=none ctermfg=135 ctermbg=233 cterm=none
"hi DiffChange       guibg=#4C4D05 gui=none ctermbg=58 cterm=none
"hi DiffAdd          guibg=#252652 gui=none ctermbg=235 cterm=none
"hi DiffText         guibg=#66336A gui=none ctermbg=241 cterm=none
"hi DiffDelete       guibg=#3F0106 gui=none ctermbg=52 cterm=none
 
hi DiffChange       guibg=#4C4C09 gui=none ctermbg=234 cterm=none
hi DiffAdd          guibg=#252556 gui=none ctermbg=17 cterm=none
hi DiffText         guibg=#66326E gui=none ctermbg=22 cterm=none
hi DiffDelete       guibg=#3F000A gui=none ctermbg=0 ctermfg=196 cterm=none
hi TabLineFill      guibg=#5E5E5E gui=none ctermbg=235 ctermfg=228 cterm=none
hi TabLineSel       guifg=#FFFFD7 gui=bold ctermfg=230 cterm=bold


" Syntax highlighting
hi Comment guifg=#F99085 gui=none ctermfg=210 cterm=none
hi Constant guifg=#C14AFF gui=none ctermfg=135 cterm=none
hi Number guifg=#C14AFF gui=none ctermfg=135 cterm=none
hi Identifier guifg=#FF86FF gui=none ctermfg=213 cterm=none
hi Statement guifg=#FF007B gui=none ctermfg=198 cterm=none
hi Function guifg=#FFD4FF gui=none ctermfg=225 cterm=none
hi Special guifg=#BE2247 gui=none ctermfg=125 cterm=none
hi PreProc guifg=#BE2247 gui=none ctermfg=125 cterm=none
hi Keyword guifg=#FF007B gui=none ctermfg=198 cterm=none
hi String guifg=#9C8EE4 gui=none ctermfg=140 cterm=none
hi Type guifg=#FF5EFF gui=none ctermfg=207 cterm=none
hi pythonBuiltin guifg=#FF86FF gui=none ctermfg=213 cterm=none
hi TabLineFill guifg=#3E3A60 gui=none ctermfg=237 cterm=none

" }}}
" Folding ----------------------------------------------------------------- {{{

set foldlevelstart=0

" Space to toggle folds.
nnoremap <Space> za
vnoremap <Space> za

" Make zO recursively open whatever fold we're in, even if it's partially open.
nnoremap zO zczO
"nnoremap <S-Space> zczO

" "Focus" the current line.  Basically:
"
" 1. Close all folds.
" 2. Open just the folds containing the current line.
" 3. Move the line to a little bit (15 lines) above the center of the screen.
" 4. Pulse the cursor line.  My eyes are bad.
"
" This mapping wipes out the z mark, which I never use.
"
" I use :sus for the rare times I want to actually background Vim.

"nnoremap <c-z> mzzMzvzz15<c-e>`z:Pulse<cr>

"function! MyFoldText() " {{{
"    let line = getline(v:foldstart)
"
"    let nucolwidth = &fdc + &number * &numberwidth
"    let windowwidth = winwidth(0) - nucolwidth - 3
"    let foldedlinecount = v:foldend - v:foldstart
"
"    " expand tabs into spaces
"    let onetab = strpart('          ', 0, &tabstop)
"    let line = substitute(line, '\t', onetab, 'g')
"
"    let line = strpart(line, 0, windowwidth - 2 -len(foldedlinecount))
"    let fillcharcount = windowwidth - len(line) - len(foldedlinecount)
"    return line . 'â€¦' . repeat(" ",fillcharcount) . foldedlinecount . 'â€¦' . ' '
"endfunction " }}}
"set foldtext=MyFoldText()

" }}}
" Filetype-specific ------------------------------------------------------- {{{

" Assembly {{{

augroup ft_asm
    au!
    au FileType asm setlocal noexpandtab shiftwidth=8 tabstop=8 softtabstop=8
augroup END

" }}}
" C {{{

augroup ft_c
    au!
    au FileType c setlocal foldmethod=marker foldmarker={,}
augroup END

" }}}
" Clojure {{{

let g:clojure_fold_extra = [
            \ 'defgauge',
            \ 'defmeter',
            \ 'defhistogram',
            \ 'defcounter',
            \ 'deftimer',
            \
            \ 'defdb',
            \ 'defentity',
            \ 'defaspect',
            \ 'add-aspect',
            \ 'defmigration',
            \
            \ 'defsynth',
            \ 'definst',
            \ 'defproject',
            \
            \ 'defroutes',
            \
            \ 'defrec',
            \
            \ 'defparser',
            \
            \ 'defform',
            \ 'defform-',
            \
            \ 'defpage',
            \ 'defsketch'
            \
            \ ]

let g:clojure_highlight_extra_defs = [
            \ 'defparser',
            \ 'deftest',
            \ 'match',
            \
            \ 'defproject',
            \
            \ 'defquery',
            \ 'defqueries',
            \
            \ 'defform',
            \
            \ 'deferror',
            \ 'when-found',
            \ 'when-valid',
            \
            \ 'defroutes'
            \ ]

let g:clojure_highlight_extra_exceptions = [
            \ 'try+',
            \ 'throw+',
            \ ]

augroup ft_clojure
    au!

    au BufNewFile,BufRead *.edn set filetype=clojure
    au BufNewFile,BufRead riemann.config set filetype=clojure

    au FileType clojure silent! call TurnOnClojureFolding()
    au FileType clojure compiler clojure
    au FileType clojure setlocal report=100000

    " Things that should be indented 2-spaced
    au FileType clojure setlocal lispwords+=when-found,defform,when-valid,try

    au FileType clojure RainbowParenthesesActivate
    au syntax clojure RainbowParenthesesLoadRound
    au syntax clojure RainbowParenthesesLoadSquare
    au syntax clojure RainbowParenthesesLoadBraces

    " Since YCM is hosefucked for Clojure, we'll use omnicompletion on <c-n>
    au FileType clojure inoremap <c-n> <c-x><c-o>

    " And close the omnicomplete preview window after we're done with it.
    au InsertLeave *.clj if pumvisible() == 0|pclose|endif

    " Friendlier Paredit mappings.
    au FileType clojure noremap <buffer> () :<c-u>call PareditWrap("(", ")")<cr>
    au FileType clojure noremap <buffer> )( :<c-u>call PareditSplice()<cr>
    au FileType clojure noremap <buffer> (( :<c-u>call PareditMoveLeft()<cr>
    au FileType clojure noremap <buffer> )) :<c-u>call PareditMoveRight()<cr>
    au FileType clojure noremap <buffer> (j :<c-u>call PareditJoin()<cr>
    au FileType clojure noremap <buffer> (s :<c-u>call PareditSplit()<cr>
    au FileType clojure noremap <buffer> [ :<c-u>call PareditSmartJumpOpening(0)<cr>
    au FileType clojure noremap <buffer> ] :<c-u>call PareditSmartJumpClosing(0)<cr>
    " )))

    " Indent top-level form.
    au FileType clojure nmap <buffer> <localleader>= mz99[(v%='z
    " ])
augroup END

" }}}
" Clojurescript {{{

augroup ft_clojurescript
    au!

    au BufNewFile,BufRead *.cljs set filetype=clojurescript
    au FileType clojurescript call TurnOnClojureFolding()

    " Indent top-level form.
    au FileType clojurescript nmap <buffer> <localleader>= v((((((((((((=%
augroup END

" }}}
" Common Lisp {{{

" function! SendToTmuxStripped(text)
"     call SendToTmux(substitute(a:text, '\v\n*$', '', ''))
" endfunction
function! SetLispWords()
    if exists("g:did_set_lisp_words")
        return
    endif

    let g:did_set_lisp_words = 1

    set lispwords+=switch
    set lispwords+=cswitch
    set lispwords+=eswitch
endfunction

augroup ft_commonlisp
    au!

    au BufNewFile,BufRead *.asd setfiletype lisp

    au FileType lisp call SetLispWords()

    " Set up some basic tslime mappings until I shave the fuckin
    " Fireplace/Common Lisp yak.
    "
    " key  desc                   mnemonic
    " \t - connect tslime         [t]slime
    " \f - send current form      [f]orm
    " \e - send top-level form    [e]val
    " \r - send entire file       [r]eload file
    " \c - send ctrl-l            [c]lear

    " Send the current form to the REPL
    au FileType lisp nnoremap <buffer> <silent> <localleader>f :let lisp_tslime_view = winsaveview()<cr>vab"ry:call SendToTmuxStripped(@r)<cr>:call winrestview(lisp_tslime_view)<cr>

    " Send the current top-level form to the REPL
    au FileType lisp nnoremap <buffer> <silent> <localleader>e :let lisp_tslime_view = winsaveview()<cr>:silent! normal! l<cr>:call PareditFindDefunBck()<cr>vab"ry:call SendToTmuxStripped(@r)<cr>:call winrestview(lisp_tslime_view)<cr>

    " Send the entire buffer to the REPL
    au FileType lisp nnoremap <buffer> <silent> <localleader>r :let lisp_tslime_view = winsaveview()<cr>ggVG"ry:call SendToTmuxStripped(@r)<cr>:call winrestview(lisp_tslime_view)<cr>

    " Clear the REPL
    au FileType lisp nnoremap <buffer> <silent> <localleader>c :call SendToTmuxRaw("")<cr>

    au FileType lisp RainbowParenthesesActivate
    au syntax lisp RainbowParenthesesLoadRound
    au syntax lisp RainbowParenthesesLoadSquare
    au syntax lisp RainbowParenthesesLoadBraces

    au FileType lisp silent! call TurnOnLispFolding()

    au FileType lisp noremap <buffer> () :<c-u>call PareditWrap("(", ")")<cr>
    au FileType lisp noremap <buffer> )( :<c-u>call PareditSplice()<cr>
    au FileType lisp noremap <buffer> (( :<c-u>call PareditMoveLeft()<cr>
    au FileType lisp noremap <buffer> )) :<c-u>call PareditMoveRight()<cr>
    au FileType lisp noremap <buffer> (j :<c-u>call PareditJoin()<cr>
    au FileType lisp noremap <buffer> (s :<c-u>call PareditSplit()<cr>
    au FileType lisp noremap <buffer> )j :<c-u>call PareditJoin()<cr>
    au FileType lisp noremap <buffer> )s :<c-u>call PareditSplit()<cr>
    au FileType lisp noremap <buffer> [[ :<c-u>call PareditSmartJumpOpening(0)<cr>
    au FileType lisp noremap <buffer> ]] :<c-u>call PareditSmartJumpClosing(0)<cr>
    " ))

    " Indent top-level form.
    au FileType lisp nmap <buffer> <localleader>= mz99[(v%='z
    " ])
augroup END

" }}}
" Confluence {{{

augroup ft_c
    au!

    au BufRead,BufNewFile *.confluencewiki setlocal filetype=confluencewiki

    " Wiki pages should be soft-wrapped.
    au FileType confluencewiki setlocal wrap linebreak nolist
augroup END

" }}}
" Cram {{{

let cram_fold=1

augroup ft_cram
    au!

    au BufNewFile,BufRead *.t set filetype=cram
    au Syntax cram setlocal foldlevel=1
    au FileType cram nnoremap <buffer> <localleader>ee :e<cr>
augroup END

" }}}
" CSS and LessCSS {{{

augroup ft_css
    au!

    au BufNewFile,BufRead *.less setlocal filetype=less

    au Filetype less,css setlocal foldmethod=marker
    au Filetype less,css setlocal foldmarker={,}
    au Filetype less,css setlocal omnifunc=csscomplete#CompleteCSS
    au Filetype less,css setlocal iskeyword+=-

    " Use <leader>S to sort properties.  Turns this:
    "
    "     p {
    "         width: 200px;
    "         height: 100px;
    "         background: red;
    "
    "         ...
    "     }
    "
    " into this:

    "     p {
    "         background: red;
    "         height: 100px;
    "         width: 200px;
    "
    "         ...
    "     }
    au BufNewFile,BufRead *.less,*.css nnoremap <buffer> <localleader>S ?{<CR>jV/\v^\s*\}?$<CR>k:sort<CR>:noh<CR>

    " Make {<cr> insert a pair of brackets in such a way that the cursor is correctly
    " positioned inside of them AND the following code doesn't get unfolded.
    au BufNewFile,BufRead *.less,*.css inoremap <buffer> {<cr> {}<left><cr><space><space><space><space>.<cr><esc>kA<bs>
augroup END

" }}}
" Django {{{

augroup ft_django
    au!

    au BufNewFile,BufRead urls.py           setlocal nowrap
    au BufNewFile,BufRead urls.py           normal! zR
    au BufNewFile,BufRead dashboard.py      normal! zR
    au BufNewFile,BufRead local_settings.py normal! zR

    au BufNewFile,BufRead admin.py     setlocal filetype=python.django
    au BufNewFile,BufRead urls.py      setlocal filetype=python.django
    au BufNewFile,BufRead models.py    setlocal filetype=python.django
    au BufNewFile,BufRead views.py     setlocal filetype=python.django
    au BufNewFile,BufRead settings.py  setlocal filetype=python.django
    au BufNewFile,BufRead settings.py  setlocal foldmethod=marker
    au BufNewFile,BufRead forms.py     setlocal filetype=python.django
    au BufNewFile,BufRead common_settings.py  setlocal filetype=python.django
    au BufNewFile,BufRead common_settings.py  setlocal foldmethod=marker
augroup END

" }}}
" DTrace {{{

augroup ft_dtrace
    au!

    autocmd BufNewFile,BufRead *.d set filetype=dtrace
augroup END

" }}}
" Firefox {{{

augroup ft_firefox
    au!
    au BufRead,BufNewFile ~/Library/Caches/*.html setlocal buftype=nofile
augroup END

" }}}
" Fish {{{

augroup ft_fish
    au!

    au BufNewFile,BufRead *.fish setlocal filetype=fish

    au FileType fish setlocal foldmethod=marker foldmarker={{{,}}}
augroup END

" }}}
" Haskell {{{

augroup ft_haskell
    au!
    au BufEnter *.hs compiler ghc
augroup END

" }}}
" HTML, Django, Jinja, Dram {{{

let g:html_indent_tags = ['p', 'li']

augroup ft_html
    au!

    au BufNewFile,BufRead *.html setlocal filetype=htmldjango
    au BufNewFile,BufRead *.dram setlocal filetype=htmldjango

    au FileType html,jinja,htmldjango setlocal foldmethod=manual

    " Use <localleader>f to fold the current tag.
    au FileType html,jinja,htmldjango nnoremap <buffer> <localleader>f Vatzf

    " Use <localleader>t to fold the current templatetag.
    au FileType html,jinja,htmldjango nmap <buffer> <localleader>t viikojozf

    " Indent tag
    au FileType html,jinja,htmldjango nnoremap <buffer> <localleader>= Vat=

    " Django tags
    au FileType jinja,htmldjango inoremap <buffer> <c-t> {%<space><space>%}<left><left><left>

    " Django variables
    au FileType jinja,htmldjango inoremap <buffer> <c-b> {{<space><space>}}<left><left><left>
augroup END

" }}}
" Java {{{

augroup ft_java
    au!

    au FileType java setlocal foldmethod=marker
    au FileType java setlocal foldmarker={,}
augroup END

" }}}
" Javascript {{{

augroup ft_javascript
    au!

    au FileType javascript setlocal foldmethod=marker
    au FileType javascript setlocal foldmarker={,}
    au FileType javascript call MakeSpacelessBufferIabbrev('clog', 'console.log();<left><left>')

    " Make {<cr> insert a pair of brackets in such a way that the cursor is correctly
    " positioned inside of them AND the following code doesn't get unfolded.
    au Filetype javascript inoremap <buffer> {<cr> {}<left><cr><space><space><space><space>.<cr><esc>kA<bs>
    " }

    " Prettify a hunk of JSON with <localleader>p
    au FileType javascript nnoremap <buffer> <localleader>p ^vg_:!python -m json.tool<cr>
    au FileType javascript vnoremap <buffer> <localleader>p :!python -m json.tool<cr>
augroup END

" }}}
" Lilypond {{{

augroup ft_lilypond
    au!

    au FileType lilypond setlocal foldmethod=marker foldmarker={,}
augroup END

" }}}
" Mail {{{

augroup ft_mail
    au!

    au Filetype mail setlocal spell
augroup END

" }}}
" Markdown {{{

augroup ft_markdown
    au!

    au BufNewFile,BufRead *.m*down setlocal filetype=markdown foldlevel=1

    " Use <localleader>1/2/3 to add headings.
    au Filetype markdown nnoremap <buffer> <localleader>1 yypVr=:redraw<cr>
    au Filetype markdown nnoremap <buffer> <localleader>2 yypVr-:redraw<cr>
    au Filetype markdown nnoremap <buffer> <localleader>3 mzI###<space><esc>`zllll
    au Filetype markdown nnoremap <buffer> <localleader>4 mzI####<space><esc>`zlllll

    au Filetype markdown nnoremap <buffer> <localleader>p VV:'<,'>!python -m json.tool<cr>
    au Filetype markdown vnoremap <buffer> <localleader>p :!python -m json.tool<cr>
augroup END

" }}}
" Mercurial {{{

augroup ft_mercurial
    au!

    au BufNewFile,BufRead *hg-editor-*.txt setlocal filetype=hgcommit
augroup END

" }}}
" Mutt {{{

augroup ft_muttrc
    au!

    au BufRead,BufNewFile *.muttrc set ft=muttrc

    au FileType muttrc setlocal foldmethod=marker foldmarker={{{,}}}
augroup END

" }}}
" Nand2Tetris HDL {{{

augroup ft_n2thdl
    au!

    au BufNewFile,BufRead *.hdl set filetype=n2thdl
augroup END

" }}}
" Nginx {{{

augroup ft_nginx
    au!

    au BufRead,BufNewFile /etc/nginx/conf/*                      set ft=nginx
    au BufRead,BufNewFile /etc/nginx/sites-available/*           set ft=nginx
    au BufRead,BufNewFile /usr/local/etc/nginx/sites-available/* set ft=nginx
    au BufRead,BufNewFile vhost.nginx                            set ft=nginx

    au FileType nginx setlocal foldmethod=marker foldmarker={,}
augroup END

" }}}
" OrgMode {{{

augroup ft_org
    au!

    au Filetype org nmap <buffer> Q vahjgq
    au Filetype org setlocal nolist
augroup END

" }}}
" Pentadactyl {{{

augroup ft_pentadactyl
    au!
    au BufNewFile,BufRead .pentadactylrc set filetype=pentadactyl
    au BufNewFile,BufRead ~/Library/Caches/TemporaryItems/pentadactyl-*.tmp set nolist wrap linebreak columns=100 colorcolumn=0
augroup END

" }}}
" Postgresql {{{

augroup ft_postgres
    au!

    au BufNewFile,BufRead *.sql set filetype=pgsql
    au BufNewFile,BufRead *.pgsql set filetype=pgsql

    au FileType pgsql set foldmethod=indent
    au FileType pgsql set softtabstop=2 shiftwidth=2
    au FileType pgsql setlocal commentstring=--\ %s comments=:--

    " Send to tmux with localleader e
    au FileType pgsql nnoremap <buffer> <silent> <localleader>e :let psql_tslime_view = winsaveview()<cr>vip"ry:call SendToTmux(@r)<cr>:call winrestview(psql_tslime_view)<cr>

    " kill pager with q
    au FileType pgsql nnoremap <buffer> <silent> <localleader>q :call SendToTmuxRaw("q")<cr>
augroup END

" }}}
" Puppet {{{

augroup ft_puppet
    au!

    au Filetype puppet setlocal foldmethod=marker
    au Filetype puppet setlocal foldmarker={,}
augroup END

" }}}
" Python {{{

augroup ft_python
    au!

    au FileType python setlocal define=^\s*\\(def\\\\|class\\)
    au FileType man nnoremap <buffer> <cr> :q<cr>

    " Jesus tapdancing Christ, built-in Python syntax, you couldn't let me
    " override this in a normal way, could you?
    au FileType python if exists("python_space_error_highlight") | unlet python_space_error_highlight | endif

    au FileType python iabbrev <buffer> afo assert False, "Okay"
augroup END

" }}}
" QuickFix {{{

augroup ft_quickfix
    au!
    au Filetype qf setlocal colorcolumn=0 nolist nocursorline nowrap tw=0
augroup END

" }}}
" ReStructuredText {{{

augroup ft_rest
    au!

    au Filetype rst nnoremap <buffer> <localleader>1 yypVr=:redraw<cr>
    au Filetype rst nnoremap <buffer> <localleader>2 yypVr-:redraw<cr>
    au Filetype rst nnoremap <buffer> <localleader>3 yypVr~:redraw<cr>
    au Filetype rst nnoremap <buffer> <localleader>4 yypVr`:redraw<cr>
augroup END

" }}}
" Riemann Config Files {{{

augroup ft_riemann
    au!

    au BufNewFile,BufRead riemann.config set filetype=clojure
    au BufNewFile,BufRead riemann.config nnoremap <buffer> <localleader>= mzgg=G`z
augroup END

" }}}
" Rubby {{{

augroup ft_ruby
    au!
    au Filetype ruby setlocal foldmethod=syntax
    au BufRead,BufNewFile Capfile setlocal filetype=ruby
augroup END

" }}}
" Scala {{{

function! DispatchMavenTest()
    let view = winsaveview()
    let zreg = @z

    " Move to the top of the file
    normal! gg

    " Find the spec name
    call search('\vclass (.*Spec)')
    normal! w"zyiw

    let spec = @z

    execute "Dispatch mvn -q -B test -Dtest=" . spec

    let @z = zreg
    call winrestview(view)
endfunction

augroup ft_scala
    au!
    au Filetype scala setlocal foldmethod=marker foldmarker={,}
    au Filetype scala setlocal textwidth=100
    au Filetype scala setlocal shiftwidth=2
    au Filetype scala compiler maven
    au Filetype scala let b:dispatch = 'mvn -B package install'
    au Filetype scala nnoremap <buffer> <localleader>s mz:%!sort-scala-imports<cr>`z
    au Filetype scala nnoremap <buffer> M :call scaladoc#Search(expand("<cword>"))<cr>
    au Filetype scala vnoremap <buffer> M "ry:call scaladoc#Search(@r)<cr>
    au Filetype scala nnoremap <buffer> <localleader>t :call DispatchMavenTest()<cr>
    au Filetype scala nmap <buffer> <localleader>( ysiwbi
    au Filetype scala nmap <buffer> <localleader>[ ysiwri
    ")]
augroup END

" }}}
" Standard In {{{

augroup ft_stdin
    au!

    " Treat buffers from stdin (e.g.: echo foo | vim -) as scratch.
    au StdinReadPost * :set buftype=nofile
augroup END

" }}}
" stevelosh.com Blog Entries {{{

augroup ft_steveloshcom
    au!
    au BufRead,BufNewFile */stevelosh/content/blog/20*/*/*.html set ft=markdown spell
    au BufRead,BufNewFile */stevelosh/content/projects/*.html set ft=markdown spell
augroup END

" }}}
" TimL {{{

" let g:timl_fold_extra = [
"             \ 'defgauge',
"             \ 'defmeter',
"             \ 'defhistogram',
"             \ 'defcounter',
"             \ 'deftimer'
"             \ ]

" let g:timl_highlight_extra_defs = [
"             \ 'defparser',
"             \ 'deftest',
"             \ 'match',
"             \
"             \ 'defroutes'
"             \ ]


augroup ft_timl
    au!

    au FileType timl silent! call TurnOnClojureFolding()

    " Things that should be indented 2-spaced
    " au FileType clojure setlocal lispwords+=when-found,defform,when-valid

    au FileType timl RainbowParenthesesActivate
    au syntax timl RainbowParenthesesLoadRound
    au syntax timl RainbowParenthesesLoadSquare
    au syntax timl RainbowParenthesesLoadBraces

    " Friendlier Paredit mappings.
    au FileType timl noremap <buffer> () :<c-u>call PareditWrap("(", ")")<cr>
    au FileType timl noremap <buffer> )( :<c-u>call PareditSplice()<cr>
    au FileType timl noremap <buffer> (( :<c-u>call PareditMoveLeft()<cr>
    au FileType timl noremap <buffer> )) :<c-u>call PareditMoveRight()<cr>
    au FileType timl noremap <buffer> (j :<c-u>call PareditJoin()<cr>
    au FileType timl noremap <buffer> (s :<c-u>call PareditSplit()<cr>
    au FileType timl noremap <buffer> [ :<c-u>call PareditSmartJumpOpening(0)<cr>
    au FileType timl noremap <buffer> ] :<c-u>call PareditSmartJumpClosing(0)<cr>
    " )))

    au FileType timl call PareditInitBuffer()

    " Indent top-level form.
    au FileType timl nmap <buffer> <localleader>= mz99[(v%='z
    " ])
augroup END

" }}}
" Vagrant {{{

augroup ft_vagrant
    au!
    au BufRead,BufNewFile Vagrantfile set ft=ruby
augroup END

" }}}
" Vim {{{

augroup ft_vim
    au!

    au FileType vim setlocal foldmethod=marker
    au FileType help setlocal textwidth=78
    au BufWinEnter *.txt if &ft == 'help' | wincmd L | endif
augroup END

" }}}
" YAML {{{

augroup ft_yaml
    au!

    au FileType yaml set shiftwidth=2
augroup END

" }}}
" XML {{{

augroup ft_xml
    au!

    au FileType xml setlocal foldmethod=manual

    " Use <localleader>f to fold the current tag.
    au FileType xml nnoremap <buffer> <localleader>f Vatzf

    " Indent tag
    au FileType xml nnoremap <buffer> <localleader>= Vat=
augroup END

" }}}

" }}}
