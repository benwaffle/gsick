var info1;
var info2;
var chattingwith;
var postscroller;
var leftscroller;
var rightscroller;
var tehusername = '';
var bottomdown;
var channel_html;
var theme_background = '';
var theme_text = '';
var theme_link = '';
var theme_input_background = '';
var theme_input_text = '';
var theme_input_border = '';
var theme_input_placeholder = '';
var theme_scroll_background = '';
var embed_option;
var lastY = 0;
var reply_to_id = 0;
var psheight;
var input_height;
var yt_players = [];
var sc_players = [];
var audio_players = [];
var video_players = [];
var vimeo_players = [];
var channel;
var loggedin;
var tehusername;
var background;
var text;
var link;
var input_background;
var input_text;
var input_border;
var input_placeholder;
var scroll_background;
var csrf_token;

function silence(uname)
{
	$.get('/silence/',
		{
			'uname':uname
		},
	function(data)
 	{
		if(data['status'] === 'ok')
		{
			msg =  "<a onClick='change_user(\"" + uname + "\");return false;' class='pm_user_link' href=\"#\">";
			msg =  msg + uname + "</a>";
			msg = msg + ' was silenced';
			dialog(msg);
			if($('#mode').val() === 'silenced')
			{
				silenced();
			}
		}
	});
	clear();
	return false;
}

function unsilence(uname)
{
	$.get('/unsilence/',
		{
			'uname':uname
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			msg =  "<a onClick='change_user(\"" + uname + "\");return false;' class='pm_user_link' href=\"#\">";
			msg =  msg + uname + "</a>";
			msg = msg + ' was unsilenced';
			dialog(msg);
			if($('#mode').val() === 'silenced')
			{
				silenced();
			}
		}
	});
	clear()
	return false;
}

function reset_players()
{
	yt_players = [];
	sc_players = [];
	vimeo_players = [];
	audio_players = [];
	video_players = [];
}

function before_back()
{
	reset_players();
}

function before_post_load()
{
	reset_players();
	if(window.history.state)
	{
		var state = window.history.state;
		state.html = $('#posts').html();
		state.scrolltop = $('#postscroller').scrollTop();
		window.history.replaceState(state, document.title);
	}
}

function after_post_load()
{	
	try
	{
		update_url();
		resize_videos();
		defocus();
		if(loggedin === 'yes')
		{
			$('#posts').ready(function()
			{
				update_theme();
			});
		}
		$('#postscroller').niceScroll().resize();
		create_yt_players();
		create_sc_players();
		create_vimeo_players();
		create_audio_players();
		create_video_players();

		if(window.history.state)
		{
			var state = window.history.state;
			state.html = $('#posts').html();
			state.scrolltop = $('#postscroller').scrollTop();
			window.history.replaceState(state, document.title);
		}
	}
	catch(err)
	{
		//
	}
}

function after_post_load_back()
{	
	try
	{
		resize_videos();
		defocus();
		if(loggedin === 'yes')
		{
			$('#posts').ready(function()
			{
				update_theme();
			});
		}
		$('#postscroller').niceScroll().resize();
		create_yt_players();
		create_sc_players();
		create_vimeo_players();
		create_audio_players();
		create_video_players();
	}
	catch(err)
	{
		//
	}
}

function silenced(post_id)
{
	$.get('/silenced/',
		{
			
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			$('#mode').val('silenced');
			$('#posts').html(data['html']);
			setHeader('silenced');
			clear();
			after_post_load();
			document.title = 'silenced';
			hide_input();
		}
	});
	clear();
	return false;
}

function open_post(post_id)
{
	$.get('/open_post/',
		{
			'post_id':post_id
		},
	function(data) 
	{
		before_post_load();
		if(data['status'] === 'ok')
		{
			$('#mode').val('channel');
			$('#posts').html(data['post']);
			setHeader('#' + data['cname']);
			clear();
			after_post_load();
			if(data['cname'] === '')
			{
				document.title = '#';
			}
			else
			{
				document.title = data['cname'];
			}
		}
		else
		{
			if(document.title === '')
			{
				random_channel();
				return false;
			}
			dialog('post didn\'t load');
		}
	});
	return false;
}

function open_user_post(post_id)
{
	$.get('/open_user_post/',
		{
			'post_id':post_id
		},
	function(data) 
	{
		before_post_load();
		if(data['status'] === 'ok')
		{
			$('#mode').val('user');
			$('#posts').html(data['post']);
			setHeader('posts by ' + data['cname']);
			clear();
			after_post_load();
			document.title = 'posts by ' + data['cname'];
		}
		else
		{
			dialog('post didn\'t load');
		}
	});
	return false;
}

function show_url()
{
	post_id = $('#channel_post:first').val();
	url = "<a href='" + document.location + "'>";
	url = url + document.location;
	url = url + "</a>";
	dialog(url);
	clear();
	return false;
}

function toTop()
{
    $('html, body').animate({scrollTop: 0}, 200);
    return false;
}

function clear()
{
    $('#inputcontent').val('');
}

function show_guest_status()
{
	msg = 'you need to ';
	msg = msg + "<a onClick='login();return false;' class='pm_user_link' href=\"#\">";
	msg = msg + 'login</a>';
	dialog(msg);
}

function rgb2hex(rgb) 
{
	o = rgb;
	try
	{
	    rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
	    function hex(x) 
	    {
	        return ("0" + parseInt(x).toString(16)).slice(-2);
	    }
	    return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);	
	}
	catch(err)
	{
		return o;
	}
}
  
function settings()
{
	if(loggedin !== 'yes')
	{
		show_guest_status();
		clear();
		return false;
	}
	if(typeof event !== 'undefined' && event.which == 2)
	{
		window.open('/settings/', "_blank");
	}
	else
	{
		$.get('/get_themes/',
			{
	        
			},
		function(data) 
		{
			before_post_load();
			$('#mode').val('settings');
			setHeader('settings');
			document.title = 'settings';
			$('#posts').html(data['html']);
			$('#posts').ready(function()
			{
				$('#cname').ready(function()
				{
					var background = rgb2hex(theme_background);
					var text = rgb2hex(theme_text);
					var link = rgb2hex(theme_link);
					var input_background = rgb2hex(theme_input_background);
					var input_text = rgb2hex(theme_input_text);
					var input_border = rgb2hex(theme_input_border);
					var input_placeholder = rgb2hex(theme_input_placeholder);
					var scroll_background = rgb2hex(theme_scroll_background);
					$('#embed_select').val(embed_option);
					$('#background_picker').ColorPicker({flat:true,color:background,onSubmit:set_background_color});
					$('#text_picker').ColorPicker({flat:true,color:text,onSubmit:set_text_color});
					$('#link_picker').ColorPicker({flat:true,color:link,onSubmit:set_link_color});
					$('#input_background_picker').ColorPicker({flat:true,color:input_background,onSubmit:set_input_background_color});
					$('#input_text_picker').ColorPicker({flat:true,color:input_text,onSubmit:set_input_text_color});
					$('#input_border_picker').ColorPicker({flat:true,color:input_border,onSubmit:set_input_border_color});
					$('#input_placeholder_picker').ColorPicker({flat:true,color:input_placeholder,onSubmit:set_input_placeholder_color});
					$('#input_scroll_background_picker').ColorPicker({flat:true,color:scroll_background,onSubmit:set_scroll_background_color});
					$( "#embed_select" ).change(function(){ embed_option = $('#embed_select').val(); set_theme(); });
				});
			});
			after_post_load();
			$('#postscroller').scrollTop(0);
			show_input('this text is called the placeholder');
		});
		clear();
	    return false;		
		
	}
}

function settings_back()
{
	$.get('/get_themes/',
		{
        
		},
	function(data) 
	{
		before_back();
		$('#mode').val('settings');
		setHeader('settings');
		document.title = 'settings';
		$('#posts').html(data['html']);
		$('#posts').ready(function()
		{
			$('#cname').ready(function()
			{
				var background = rgb2hex(theme_background);
				var text = rgb2hex(theme_text);
				var link = rgb2hex(theme_link);
				var input_background = rgb2hex(theme_input_background);
				var input_text = rgb2hex(theme_input_text);
				var input_border = rgb2hex(theme_input_border);
				var input_placeholder = rgb2hex(theme_input_placeholder);
				var scroll_background = rgb2hex(theme_scroll_background);
				$('#background_picker').ColorPicker({flat:true,color:background,onSubmit:set_background_color});
				$('#text_picker').ColorPicker({flat:true,color:text,onSubmit:set_text_color});
				$('#link_picker').ColorPicker({flat:true,color:link,onSubmit:set_link_color});
				$('#input_background_picker').ColorPicker({flat:true,color:input_background,onSubmit:set_input_background_color});
				$('#input_text_picker').ColorPicker({flat:true,color:input_text,onSubmit:set_input_text_color});
				$('#input_border_picker').ColorPicker({flat:true,color:input_border,onSubmit:set_input_border_color});
				$('#input_placeholder_picker').ColorPicker({flat:true,color:input_placeholder,onSubmit:set_input_placeholder_color});
				$('#input_scroll_background_picker').ColorPicker({flat:true,color:scroll_background,onSubmit:set_scroll_background_color});
			});
		});
		after_post_load_back();
		$('#postscroller').scrollTop(0);
		show_input('this text is called the placeholder');
	});
	clear();
    return false;		
}

function set_background_color(hsb,hex,rgb)
{
	theme_background = '#' + hex;
	update_theme();
	set_theme();
}

function set_text_color(hsb,hex,rgb)
{
	theme_text = '#' + hex;
	update_theme();
	set_theme();
}

function set_link_color(hsb,hex,rgb)
{
	theme_link = '#' + hex;
	update_theme();
	set_theme();
}

function set_input_background_color(hsb,hex,rgb)
{
	theme_input_background = '#' + hex;
	update_theme();
	set_theme();
}

function set_input_text_color(hsb,hex,rgb)
{
	theme_input_text = '#' + hex;
	update_theme();
	set_theme();
}

function set_input_border_color(hsb,hex,rgb)
{
	theme_input_border = '#' + hex;
	update_theme();
	set_theme();
}

function set_input_placeholder_color(hsb,hex,rgb)
{
	theme_input_placeholder = '#' + hex;
	update_theme();
	set_theme();
}

function set_scroll_background_color(hsb,hex,rgb)
{
	theme_scroll_background = '#' + hex;
	update_theme();
	set_theme();
}

function set_default_theme()
{
	theme_background = '';
	theme_text = '';
	theme_link = '';
	theme_input_background = '';
	theme_input_text = '';
	theme_input_placeholder = '';
	theme_input_border = '';
	theme_scroll_background = '';
	set_theme_and_reload();
}

function set_theme()
{
	$.post('/set_theme/',
	{
    	csrfmiddlewaretoken: csrf_token,
    	theme_background:theme_background,
    	theme_text:theme_text,
    	theme_link:theme_link,
    	theme_input_background:theme_input_background,
    	theme_input_text:theme_input_text,
    	theme_input_border:theme_input_border,
    	theme_input_placeholder:theme_input_placeholder,
    	theme_scroll_background:theme_scroll_background,
    	embed_option:embed_option,
	},
	function(data) 
	{
		
	});
    return false;	
}

function set_theme_and_reload()
{
	$.post('/set_theme/',
	{
    	csrfmiddlewaretoken: csrf_token,
    	theme_background:theme_background,
    	theme_text:theme_text,
    	theme_link:theme_link,
    	theme_input_background:theme_input_background,
    	theme_input_text:theme_input_text,
    	theme_input_border:theme_input_border,
    	theme_input_placeholder:theme_input_placeholder,
    	theme_scroll_background:theme_scroll_background,
    	embed_option:embed_option,
	},
	function(data) 
	{
		window.location.reload()
	});
    return false;	
}

function update_theme()
{
	if(loggedin !== 'yes')
	{
		return false;
	}
	if(theme_background !== '')
	{
		$('body').css('background-color',theme_background);
		$('html').css('background-color',theme_background);
		$('.threecol').css('background-color',theme_background);
		$('.colmid').css('background-color',theme_background);
		$('.colleft').css('background-color',theme_background);
		$('#centercol').css('background-color',theme_background);	
	}
	if(theme_link !== '')
	{
		$('a').css('color',theme_link);
	}
	if(theme_text !== '')
	{
		$('body').css('color',theme_text);
		$('html').css('color',theme_text);
		$('.cname').css('color',theme_text);
		$('.details').css('color',theme_text);
	}
	if(theme_input_background !== '')
	{
		$('#inputcontent').css('background-color', theme_input_background)
		$('.alert_reply_input').css('background-color', theme_input_background)
	}
	if(theme_input_text !== '')
	{
		$('#inputcontent').css('color', theme_input_text)
		$('.alert_reply_input').css('color', theme_input_text)
	}
	if(theme_input_border !== '')
	{
		$('#inputcontent').css('border-color', theme_input_border)
		$('.alert_reply_input').css('border-color', theme_input_border)
	}
	if(theme_input_placeholder !== '')
	{
		var styleContent = 'input:-moz-placeholder {color: ' + theme_input_placeholder + ';} input::-moz-placeholder {color: ' + theme_input_placeholder + ';} input::-webkit-input-placeholder {color: ' + theme_input_placeholder + ';} input:-ms-input-placeholder {color: ' + theme_input_placeholder + ';}';
		$('#placeholder-style').text(styleContent);
	}
	if(theme_scroll_background !== '')
	{
		$('.nicescroll-cursors').css('background-color', theme_scroll_background)
	}
	if(theme_background !== '' && theme_text !== '')
	{
		$('.quote_body').css('background-color', theme_text);
		$('.quote_body').css('color', theme_background);
		$('.quote_username:link').css('color', theme_background);
		$('.quote_username:visited').css('color', theme_background);
		$('.quote_username:hover').css('color', theme_background);
	}
}

function notes()
{
	if(loggedin !== 'yes')
	{
		show_guest_status();
		clear();
		return false;
	}
	$.get('/get_notes/',
		{
        
		},
	function(data) 
	{
		before_post_load();
		if(data['status'] === 'ok')
		{
			$('#mode').val('notes');
			$('#posts').html(data['notes']).ready(function()
			{
			});
			setHeader('notes');
			clear();
			after_post_load();
			$('#postscroller').scrollTop(0);
			document.title = 'notes';
			show_input('make a note')
		}
		else
		{
			
		}
	});
	clear();
    return false;	
}

function new_note()
{
	$('#inputcontent').focus().val('note: ');
}

function alerts()
{
	if(loggedin !== 'yes')
	{
		show_guest_status();
		clear();
		return false;
	}
	if(typeof event !== 'undefined' && event.which == 2)
	{
		window.open('/alerts/', "_blank");
	}
	else
	{
		$.get('/view_alerts/',
			{
	        
			},
		function(data) 
		{
			before_post_load();
			$('#mode').val('alerts');
			$('#posts').html(data['alerts']).ready(function()
			{
			});
			setHeader('alerts');
			$('#postscroller').scrollTop(0);
			document.title = 'alerts';
			after_post_load();
			$('#menu_alerts').html('alerts');
			hide_input();
		});
		clear();
	    return false;	
	}
}

function alerts_back(h)
{
	before_back();
	$('#mode').val('alerts');
	$('#posts').html(h.html).ready(function()
	{
	});
	setHeader('alerts');
	$('#postscroller').scrollTop(h.scrolltop);
	document.title = 'alerts';
	after_post_load_back();
	hide_input();
	clear();
}

function reply_to(id)
{
	if(loggedin !== 'yes')
	{
		show_guest_status();
		clear();
		return false;
	}
	reply_to_id = id;
	$('#inputcontent').focus().val('reply: ');
    return false;	
}

function reply(input)
{
	if(loggedin !== 'yes')
	{
		show_guest_status();
		clear();
		return false;
	}
	post_id = $('.post_id:first').val();
	$.post('/reply/',
		{
			input:input,
			post_id:post_id,
			reply_to_id:reply_to_id,
			csrfmiddlewaretoken:csrf_token
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			go_to_bottom();
		}
	});
	clear();
    return false;	
}

function reply_to_comment(msg, comment_id, goto_bottom)
{
	if(loggedin !== 'yes')
	{
		show_guest_status();
		clear();
		return false;
	}
	$.post('/reply_to_comment/',
		{
			msg:msg,
			comment_id:comment_id,
			csrfmiddlewaretoken: csrf_token
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			if(goto_bottom)
			{
				go_to_bottom()
			}
			else
			{
				$('.alert_reply_input').each(function()
				{
					$(this).val('');
				})
				dialog('reply sent')
			}
		}
	});
	clear();
    return false;	
}

function chatall()
{
	if(typeof event !== 'undefined' && event.which == 2)
	{
		window.open('/chat/', "_blank");
	}
	else
	{
		if(loggedin !== 'yes')
		{
			show_guest_status();
			clear();
			return false;
		}
		$.get('/view_chat/',
			{
	        
			},
		function(data) 
		{
			before_post_load();
			$('#mode').val('chatall');
			$('#posts').html(data['posts'])
			setHeader('chat');
			document.title = 'chat';
			after_post_load();
			$('#postscroller').scrollTop(0);
			$('#menu_chat').html('chat');
			hide_input();
		});
		clear();
	    return false;	
	}
}

function chatall_back()
{
	$.get('/view_chat/',
		{
        
		},
	function(data) 
	{
		before_back();
		$('#mode').val('chatall');
		$('#posts').html(data['posts'])
		setHeader('chat');
		document.title = 'chat';
		after_post_load_back();
		$('#postscroller').scrollTop(0);
		$('#menu_chat').html('chat');
		hide_input();
	});
	clear();
    return false;	
}

function sent()
{
	if(loggedin !== 'yes')
	{
		show_guest_status();
		clear();
		return false;
	}
	$.get('/sent_messages/',
		{
        
		},
	function(data) 
	{
		$('#mode').val('sent');
		$('#posts').html(data['posts']).ready(function()
		{
		});
		setHeader('sent');
		clear();
		after_post_load();
		$('#postscroller').scrollTop(0);
		document.title = 'sent';
		hide_input();
	});
	clear();
    return false;	
}

function chat(username)
{
	if(loggedin !== 'yes')
	{
		show_guest_status();
		clear()
		return false;
	}
	if(typeof event !== 'undefined' && event.which == 2)
	{
		window.open('/chat/' + username, "_blank");
	}
	else
	{
		$.get('/chat_with/',
			{
	        username:username
			},
		function(data) 
		{
			before_post_load();
			if(data['status'] === 'ok')
			{
				chattingwith = data['username'];
				info1 = chattingwith;
				$('#posts').html(data['posts'])
				$('#mode').val('chat');
				setHeader('chat with ' + '<a onClick="change_user(\''+data['username']+'\');return false;" href="#">' + data['username'] + '</a>');
				document.title = 'chat with ' + data['username'];
				after_post_load();
				$('#postscroller').scrollTop(0);
				show_input('write a message');
			}
			else
			{
				dialog('user does not exist');
			}
		});
		clear();
	    return false;	
	}
}

function chat_back(username)
{
	$.get('/chat_with/',
		{
        username:username
		},
	function(data) 
	{
		before_back();
		if(data['status'] === 'ok')
		{
			chattingwith = data['username'];
			info1 = chattingwith;
			$('#posts').html(data['posts'])
			$('#mode').val('chat');
			setHeader('chat with ' + '<a onClick="change_user(\''+data['username']+'\');return false;" href="#">' + data['username'] + '</a>');
			document.title = 'chat with ' + data['username'];
			after_post_load_back();
			$('#postscroller').scrollTop(0);
			show_input('write a message');
		}
		else
		{
			dialog('user does not exist');
		}
	});
	clear();
    return false;
}

function message()
{
	$('#inputcontent').focus().val('message: ');
}

function refresh_chat()
{
	id = $('#chat_post:first').attr('value')
	if(id)
	{

	}
	else{
		id = 0;
	}
	$.get('/refresh_chat/',
	 {
	 	first_chat_id:id,
	 	username:chattingwith
	 },
	function(data)
	{
		if(data['status'] === "ok")
		{
            $(data['posts']).hide().prependTo('#posts').fadeIn('slow').ready(function()
        	{
			after_post_load();
        	});
		}
		return false;
	});
	return false;
}

function refresh_chatall()
{
	id = $('#chat_post:first').attr('value')
	if(id)
	{

	}
	else{
		id = 0;
	}
	$.get('/refresh_chatall/',
	 {
	 	first_chat_id:id,
	 },
	function(data)
	{
		if(data['status'] === "ok")
		{
            $(data['messages']).hide().prependTo('#posts').fadeIn('slow').ready(function()
        	{
        		remove_duplicate_chatall();
        	});
			after_post_load();
		}
		return false;
	});
	return false;
}

function refresh_sent()
{
	id = $('#chat_post:first').attr('value')
	if(id)
	{

	}
	else{
		id = 0;
	}
	$.get('/refresh_sent/',
	 {
	 	first_chat_id:id,
	 },
	function(data)
	{
		if(data['status'] === "ok")
		{
            $(data['messages']).hide().prependTo('#posts').fadeIn('slow').ready(function()
        	{
        		remove_duplicate_sent_receivers();
        	});
			after_post_load();
		}
		return false;
	});
	return false;
}

function note(note)
{
	if (loggedin !== 'yes')
	{
		clear();
		show_guest_status();
		dialog (msg);
		return false;
	}
	$.post('/note/',
		{
        note:note,
        csrfmiddlewaretoken: csrf_token
		},
	function(data) 
	{
        if($('#mode').val() === 'notes')
        {
        	notes();
        }
        else
        {
        	dialog('note saved');
        }
	});
	clear();
    return false;		
}

function seen(uname)
{
	$.get('/seen/',
		{
        uname:uname
		},
	function(data) 
	{
        var msg = "";
        if(data!="")
        {
            msg =  "<a onClick='change_user(\"" + data['uname'] + "\");return false;' class='pm_user_link' href=\"#\">";
            msg = msg + data['uname'] + "</a> was seen " + data['date'];
        }
        else{
            msg = "I have not seen " + uname;
        }
        dialog(msg);
        clear();
        return false;
	});
    return false;
}

function activate_timeago()
{
	$('.timeago').each(function()
	{
		var $this = $(this);
		if ($this.data('active')!='yes')
		{
			$this.timeago().data('active','yes');    
		}
	});
	setTimeout(activate_timeago, 60000);
}

var dialog = (function() 
{
    var timer; 
    return function(msg, options) 
    {
        clearTimeout(timer);
        s = "<div'>" + msg + "</div>";
        $('#cname').html(s);
        update_theme();
        timer = setTimeout(function() 
        {
            $('#cname').html(channel_html);
            update_theme();
        }, 4000);
    };
})();

var bottomtimer = (function() 
{
    var timer; 
    return function() 
    {
        clearTimeout(timer);
        timer = setTimeout(function() 
        {
            bottomdown = false;
        }, 1000);
    };
})();

function load_more()
{
	mode = $('#mode').val()
	if(mode === 'channel')
	{
		load_more_channel();
	}
	if(mode === 'user')
	{
		load_more_user();
	}
	if(mode === 'notes')
	{
		load_more_notes();
	}
	else if(mode === 'chat')
	{
		load_more_chat();
	}
	else if(mode === 'chatall')
	{
		load_more_chatall();
	}
	else if(mode === 'sent')
	{
		load_more_sent();
	}
	else if(mode === 'inbox')
	{
		load_more_inbox();
	}
	else if(mode === 'stream')
	{
		load_more_stream();
	}
	else if(mode === 'new')
	{
		load_more_new();
	}
	else if(mode === 'post')
	{
		load_more_comments();
	}
	else if(mode === 'pins')
	{
		load_more_pins();
	}
	else if(mode === 'alerts')
	{
		load_more_alerts();
	}
	else if(mode === 'useronchannel')
	{
		load_more_useronchannel();
	}
}

function pin(id)
{
	if(loggedin !== 'yes')
	{
		show_guest_status();
		clear();
		return false;
	}
	$.post('/pin_post/',
		{
			id: id,
			csrfmiddlewaretoken: csrf_token
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			if($('#mode').val() === 'post')
			{
				$('#posts').find('.pins_status').html('appreciated (' + data['num_pins'] + ')')
			}
			else
			{
				$('#post_' + id).find('.pins_status').html('appreciated (' + data['num_pins'] + ')')
			}
		}
	});
	return false;	
}

function my_pins()
{
	get_pins(tehusername);
}

function get_pins(uname)
{
	if(uname === '')
	{
		show_guest_status();
		return false;
	}
	if(typeof event !== 'undefined' && event.which == 2)
	{
		window.open('/pins/' + uname, "_blank");
	}
	else
	{
		$.get('/get_pins/',
			{
				uname: uname
			},
		function(data) 
		{
			before_post_load();
			if(data['status'] === 'ok')
			{
				$('#mode').val('pins');
				$('#posts').html(data['pins']).ready(function()
				{
				});
				if(data['uname'] === tehusername)
				{
					setHeader('pins');
					document.title = 'pins';
				}
				else
				{
					if(loggedin !== 'yes')
					{
						setHeader('pins by ' + data['uname'] 
							      + ' | <a onClick="change_user(\''+data['uname']+'\');return false;" href="#">posts</a>' 
							      + ' | <a onClick="chat(\''+data['uname']+'\');return false;" href="#">chat</a>');
					}
					else
					{
						setHeader('pins by ' + data['uname'] 
							      + ' | <a onClick="change_user(\''+data['uname']+'\');return false;" href="#">posts</a>' 
							      + ' | <a onClick="chat(\''+data['uname']+'\');return false;" href="#">chat</a>'
							      + ' | <a id="following_status" onClick="toggle_follow(\''+data['uname']+'\');return false;" href="#">' + data['following'] + '</a>');
					}
					document.title = 'pins by ' + data['uname'];
				} 
				info1 = data['uname'];
				after_post_load();
				$('#postscroller').scrollTop(0);
				hide_input();
			}
		});
		clear();
		return false;	
	}
}

function get_pins_back(h)
{
	before_back();
	$('#mode').val('pins');
	$('#posts').html(h.html).ready(function()
	{
	});
	if(h.info === tehusername)
	{
		setHeader('pins');
		document.title = 'pins';
	}
	else
	{
		setHeader('pins by ' + h.info 
			      + ' | <a onClick="change_user(\''+h.info+'\');return false;" href="#">posts</a>' 
			      + ' | <a onClick="chat(\''+h.info+'\');return false;" href="#">chat</a>');
		document.title = 'pins by ' + h.info;
	} 
	info1 = h.info;
	after_post_load_back();
	$('#postscroller').scrollTop(h.scrolltop);
	hide_input();
	clear();
}

function load_more_alerts()
{
	id = $('.alert_id:last').val();
	$.get('/load_more_alerts/',
		{
			id: id
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			$(data['alerts']).hide().appendTo('#posts').fadeIn('slow').ready(function()
			{
			});
			after_post_load();
		}
		bottomdown = false;
	});
	return false;
}

function load_more_channel()
{
	ids = get_posts_ids();
	$.get('/load_more_channel/',
	{
		ids: ids
	},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			$(data['posts']).hide().appendTo('#posts').fadeIn('slow').ready(function()
			{
			});
			after_post_load();
		}
		bottomdown = false;
	});
	return false;
}

function load_more_useronchannel()
{
	$.get('/load_more_useronchannel/',
		{
			id: $('.post_id:last').val(),
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			$(data['posts']).hide().appendTo('#posts').fadeIn('slow').ready(function()
			{
			});
			after_post_load();
		}
		bottomdown = false;
	});
	return false;
}

function load_more_comments()
{
	id = $('.post_id:first').val();
	last_id = $('.comment_id:last').val();
	$.get('/load_more_comments/',
		{
			id: id,
			last_id: last_id
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			$(data['comments']).appendTo('#posts');
			after_post_load();
		}
		bottomdown = false;
	});
	return false;
}

function load_more_pins()
{
	id = $('.pin_id:last').val();
	$.get('/load_more_pins/',
		{
			id: id,
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			$(data['pins']).appendTo('#posts');
			after_post_load();
		}
		bottomdown = false;
	});
	return false;
}

function load_more_user()
{
	id = $('.post_id:last').val();
	$.get('/load_more_user/',
		{
			id: id
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			$(data['posts']).hide().appendTo('#posts').fadeIn('slow').ready(function()
			{
			});
			after_post_load();
		}
		bottomdown = false;
	});
	return false;
}

function load_more_chatall()
{
	last_pm_id = $('.id:last').val();
	$.get('/load_more_chatall/',
		{
			last_pm_id: last_pm_id
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			messages = data['messages'];
			$(messages).hide().appendTo('#posts').fadeIn('slow').ready(function()
			{
			});
			after_post_load();
		}
		bottomdown = false;
	});
	return false;
}

function load_more_chat()
{
	last_pm_id = $('.id:last').val();
	$.get('/load_more_chat/',
		{
			last_pm_id: last_pm_id
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			messages = data['messages']
			$(messages).hide().appendTo('#posts').fadeIn('slow').ready(function()
			{
			});
			after_post_load();
		}
		bottomdown = false;
	});
	return false;
}

function load_more_inbox()
{
	last_pm_id = $('.id:last').val();
	$.get('/load_more_inbox/',
		{
			last_pm_id: last_pm_id
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			messages = data['messages'];
			$(messages).hide().appendTo('#posts').fadeIn('slow').ready(function()
			{
			});
			after_post_load();
		}
		bottomdown = false;
	});
	return false;
}

function load_more_sent()
{
	last_pm_id = $('.id:last').val();
	$.get('/load_more_sent/',
		{
			last_pm_id: last_pm_id
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			messages = data['messages'];
			$(messages).hide().appendTo('#posts').fadeIn('slow').ready(function()
			{
			});
			after_post_load();
		}
		bottomdown = false;
	});
	return false;
}

function load_more_notes()
{
	last_note_id = $('.id:last').val();
	$.get('/load_more_notes/',
		{
			last_note_id: last_note_id
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			notes = data['notes'];
			$(notes).hide().appendTo('#posts').fadeIn('slow').ready(function()
			{
			});
			after_post_load();
		}
		bottomdown = false;
	});
	return false;
}

function whoami()
{
	if(loggedin !== 'yes')
	{
		msg = 'you are a guest';
		dialog(msg);
		clear();
		return false;
	}
	$.get('/whoami/',
		{
		},
	function(data) 
	{
        var msg = "";
        msg = msg + "you are ";
		msg = msg + "<a onClick='change_user(\"" + data + "\");return false;' class='pm_user_link' href=\"#\">";
		msg = msg + data + "</a>"
        dialog(msg);
		clear();
        return false;
	});
    return false;
}

function calculator(operation, result)
{
    var msg = "";
    dialog(result);
    clear();
    return false;
}

function close_tab()
{
	window.open('', '_self', '');
	window.close();
	return false;
}

function open_tab()
{
	clear();
	window.open(document.location, "_blank");	
	return false;
}

function send_global_pm()
{
	$.get('/send_global_pm/',
		{
		message:$('#inputcontent').val().substring(7)
		},
	function(data) 
	{
		refresh_pm();
		clear();
	});
	return false;
}

function get_help()
{
	$.get('/get_help/',
		{
		},
	function(data) 
	{
		$('#posts').html(data['help']);
		setHeader('help');
		$('#mode').val('help');
		clear();
		after_post_load();
		$('#postscroller').scrollTop(0);
		document.title = 'help';
	});
	return false;
}

function channel_listener()
{
	var posts = document.getElementById('posts');
	if(window.addEventListener) 
	{
	   posts.addEventListener('DOMSubtreeModified', c1, false);
	} else if(window.attachEvent) 
	{
		  posts.attachEvent('DOMSubtreeModified', c1);
	   }
	function c1() 
	{
	}
}

function check_images()
{
	$('#posts img').each(function()
	{
		$(this).error(function()
		{
			content = $(this).closest('.post_content');
			container = $(this).closest('.post_parent');
			$(this).closest('a').remove();
			if(content.html() === '')
			{
				container.remove();
			}
			return false;
		});
		$(this).load(function()
		{
			if($(this).height() > $(this).closest('.image_parent').height())
			{
				var s = "<div class='too_long_text'> (image is too long, click it to see it in full size) </div>";
				if($(this).closest('.post_parent').find('.too_long_text').length < 1)
				{
					$(this).closest('.image_parent').after(s)
				}
			}
		})
	});
}

function go_to_bottom()
{
	show_last_comments();
}

function login()
{
	window.location.replace('/enter');	
	return false;
}

function open_post(id)
{
	if(typeof event !== 'undefined' && event.which == 2)
	{
		window.open('/post/' + id, "_blank");
	}
	else
	{
		$.get('/open_post/',
		{
	        id: id
		},
		function(data) 
		{
			before_post_load();
			$('#mode').val('post');
			$('#posts').html(data['post']);
			$(data['comments']).appendTo('#posts');
			setHeader('a post on <a onClick="change_channel(\''+data['cname']+'\');return false;" href="#">' + data['cname'] + '</a>');
			clear();
			channel = data['cname'];
			document.title = 'a post on ' + channel;
			$('#postscroller').scrollTop(0);
			after_post_load();
			show_input('write a comment');
		});
		return false;
	}
}

function random_post()
{
	if(typeof event !== 'undefined' && event.which == 2)
	{
		window.open('/random/', "_blank");
	}
	else
	{
		$.get('/random_post/',
			{

			},
		function(data) 
		{
			before_post_load();
			$('#mode').val('post');
			$('#posts').html(data['post']);
			$(data['comments']).appendTo('#posts');
			setHeader('a post on <a onClick="change_channel(\''+data['cname']+'\');return false;" href="#">' + data['cname'] + '</a>');
			clear();
			channel = data['cname'];
			document.title = 'a post on ' + channel;
			$('#postscroller').scrollTop(0);
			after_post_load();
			show_input('write a comment');
		});
		return false;
	}
}

function open_post_back(h)
{
	before_back();
	$('#mode').val('post');
	$('#posts').html(h.html);
	setHeader('a post on <a onClick="change_channel(\'' + h.channel + '\');return false;" href="#">' + h.channel + '</a>');
	channel = h.channel;
	document.title = 'a post on ' + channel;
	$('#postscroller').scrollTop(h.scrolltop);
	after_post_load_back();
	show_input('write a comment');
	clear();
}

function setHeader(html)
{
	channel_html = '<div class="cname">' + html + '</div>';
	$('#cname').html(channel_html);
}

function start_left_menu()
{
	s = ''
	s = s + "<div class='unselectable' style='padding-top:50px'>"
	s = s + "<div class='menu_link'><a onClick='stream();return false;' href='#'>stream</a></div>";
	s = s + "<div class='menu_link'><a onClick='show_goto();return false;' href='#'>goto</a></div>";
	s = s + "<div class='menu_link'><a onClick='top_posts();return false;' href='#'>top</a></div>";
	s = s + "<div class='menu_link'><a onClick='new_posts();return false;' href='#'>new</a></div>";
	s = s + "<div class='menu_link'><a class='menu_link' onClick='window.history.back();return false' href='#'>back</a></div>";
	s = s + "</div>"
	$('#leftcol').html(s);
}

function start_right_menu()
{
	s = ''
	s = s + "<div class='unselectable' style='text-align:right;padding-top:50px'>"
	s = s + "<div class='menu_link'><a onClick='my_history();return false;' href='#'>posts</a></div>";
	s = s + "<div class='menu_link'><a onClick='my_pins();return false;' href='#'>pins</a></div>";
	s = s + "<div class='menu_link'><a onClick='chatall();return false;' href='#'><div style='display:inline-block' id='menu_chat'>chat</div></a></div>";
	s = s + "<div class='menu_link'><a onClick='alerts();return false;' href='#'><div style='display:inline-block' id='menu_alerts'>alerts</div></a></div>";
	s = s + "<div class='menu_link'><a onClick='settings();return false;' href='#'>settings</a></div>";
	s = s + "</div>"
	$('#rightcol').html(s);
}

function random_channel()
{
	$.get('/random_channel/',
		{
        current: document.title
		},
	function(data) 
	{
		before_post_load();
		$('#mode').val('channel');
		$('#posts').html(data['posts']);
		s = data['cname'];
		setHeader(s)
		channel = data['cname']
		document.title = channel;
		after_post_load();
		show_input('post to the channel');
		clear();
	});
	return false;
}

function post_comment(content)
{
	if(loggedin !== 'yes')
	{
		show_guest_status();
		clear();
		return false;
	}
	id = $('.post_id:first').val();
	$.post('/post_comment/',
		{
        	content: content,
        	id:id,
        	csrfmiddlewaretoken: csrf_token
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			show_last_comments();
		}
		if(data['status'] === 'duplicate')
		{
			dialog('you posted that already');
		}
		clear();
	});
	return false;	
}

function show_last_comments()
{
	id = $('.post_id:first').val();
	$.get('/show_last_comments/',
		{
		id:id
		},
	function(data) 
	{
		before_post_load();
		$('#mode').val('post');
		$('#posts').html(data['comments']).ready(function()
		{
			if($('#posts').find("img").length > 0)
			{
				if($('#posts').find('iframe').length > 0)
				{
					$('#posts').find('iframe').ready(function()
					{
						$('#posts').find('img').load(function()
						{
							$('#postscroller').scrollTop($('#postscroller').get(0).scrollHeight);
						});
					})
					$('#posts').find('iframe').load(function()
					{
						$('#posts').find('img').load(function()
						{
							$('#postscroller').scrollTop($('#postscroller').get(0).scrollHeight);
						});
					})
				}
				else
				{
					$('#posts').find('img').load(function()
					{
						$('#postscroller').scrollTop($('#postscroller').get(0).scrollHeight);
					});
				}
			}
			else
			{
				if($('#posts').find('iframe').length > 0)
				{
					$('#posts').find('iframe').ready(function()
					{
						$('#postscroller').scrollTop($('#postscroller').get(0).scrollHeight);
					})
					$('#posts').find('iframe').load(function()
					{
						$('#postscroller').scrollTop($('#postscroller').get(0).scrollHeight);
					})
				}
				else
				{
					$('#postscroller').scrollTop($('#postscroller').get(0).scrollHeight);
				}
			} 
		})
		setHeader('a post on <a onClick="change_channel(\''+data['cname']+'\');return false;" href="#">' + data['cname'] + '</a>');
		channel = data['cname'];
		document.title = 'a post on ' + channel;
		after_post_load();
		show_input('write a comment')
		clear();
	});
	clear();
	return false;
}

function comment()
{
	$('#inputcontent').focus().val('comment: ');
}

function show_older_comments()
{
	id = $('.comment_id:first').val();
	$.get('/show_older_comments/',
		{
		id:id
		},
	function(data) 
	{
		$(data['comments']).prependTo('#posts');
		after_post_load();
	});
	return false;
}

function post_to_channel()
{
	if(loggedin !== 'yes')
	{
		show_guest_status();
		clear();
		return false;
	}
	if(document.title === "help" || document.title === "notes")
	{
		return false;
	}
	content = $('#inputcontent').val();
    $.post('/post_to_channel/', { channel:channel, content:content, csrfmiddlewaretoken:csrf_token }, function(data)
    {
		if(data['status'] === "ok")
		{
			change_channel(document.title);
		}
		else if(data['status'] === 'wait')
		{
			dialog('you can post in this channel once every 12 hours');
		}
		else if(data['status'] === 'channelduplicate')
		{
			dialog('that was already posted in this channel');
		}
		else if(data['status'] === 'toobig')
		{
			dialog('a post cannot exceed 2000 characters');
		}
		else if(data['status'] === 'postduplicate')
		{
			dialog('you posted that already');
		}
		clear();
        return false;
    });
}

function change_channel(cname)
{
	if(typeof event !== 'undefined' && event.which == 2)
	{
		window.open('/' + cname, "_blank");
	}
	else
	{
		if(cname === 'stream')
		{
			stream();
			return false;
		}
		if(cname === 'new')
		{
			new_posts();
			return false;
		}
		if(cname === 'top')
		{
			top_posts();
			return false;
		}
		if(cname === 'random')
		{
			random_post();
			return false;
		}
		if(cname === 'posts')
		{
			my_history();
			return false;
		}
		if(cname === 'pins')
		{
			my_pins();
			return false;
		}
		if(cname === 'alerts')
		{
			alerts();
			return false;
		}
		if(cname === 'settings')
		{
			settings();
			return false;
		}
		if(cname === 'chat')
		{
			chatall();
			return false;
		}
		if(cname === 'logout')
		{
			login();
			return false;
		}
		if(cname === 'back')
		{
			go_back();
			return false;
		}
		$.get('/get_channel/',
		{
			cname: cname
		},
		function(data) 
		{
			before_post_load();
			if(data['status'] === 'ok')
			{
				$('#mode').val('channel');
				$('#posts').html(data['posts']);
				setHeader(data['cname']);
				$('#postscroller').scrollTop(0);
				channel = data['cname']
				document.title = channel;
				after_post_load();
				show_input('post to the channel');
			}
		});
		clear();
		return false;
	}
}

function change_channel_back(h)
{
	before_back();
	$('#mode').val('channel');
	$('#posts').html(h.html);
	setHeader(h.info);
	$('#postscroller').scrollTop(h.scrolltop);
	channel = h.info
	document.title = channel;
	after_post_load_back();
	show_input('post to the channel');
	clear();
}

function hide_overlay()
{
	$('#overlay').css('display', 'none')
	$('#goto_dialog').css('display', 'none')
	$('#goto_input').val('')
	$('#channel_list').html('')
}


function show_goto()
{
	$('#overlay').css('display', 'block')
	$('#goto_dialog').css('display', 'block')
	$('#goto_input').focus()
	$.get('/get_channel_list/',
		{
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			activate_channel_list_scroll();
			$('#channel_list').html(data['channels']);
		}
	});	
}

function activate_channel_list_scroll()
{
	$('#channel_list_scroller').getNiceScroll().remove()
	$('#channel_list_scroller').niceScroll({zindex:99999,mousescrollstep:20,autohidemode:'hidden',enablemousewheel:true,horizrailenabled:false});
}

function defocus()
{
	if($('#inputcontent').val() === '')
	{
		$('#inputcontent').blur();
	}
}

function change_user(uname)
{
	if(typeof event !== 'undefined' && event.which == 2)
	{
		window.open('/user/' + uname, "_blank");
	}
	else
	{
		$.get('/get_user/',
			{
			uname: uname
			},
		function(data) 
		{
			before_post_load();
			if(data!="")
			{
				$('#posts').html(data['posts']);
				$('#mode').val('user');
				if(data['uname'] === tehusername)
				{
					setHeader('posts');
					document.title = 'posts'				
				}
				else
				{
					if(loggedin !== 'yes')
					{
						setHeader('posts by ' + data['uname']);
					}
					else
					{
						setHeader('posts by ' + data['uname'] 
						       + ' | <a onClick="chat(\''+data['uname']+'\');return false;" href="#">chat</a>'
							   + ' | <a id="following_status" onClick="toggle_follow(\''+data['uname']+'\');return false;" href="#">' + data['following'] + '</a>');
					}
					document.title = 'posts by ' + data['uname'];
				}
				info1 = data['uname'];
				after_post_load();
				$('#postscroller').scrollTop(0);
				hide_input();
			}
		});
		clear();
		return false;
	}
}

function change_user_back(h)
{
	before_back();
	$('#posts').html(h.html);
	$('#mode').val('user');
	if(h.info === tehusername)
	{
		setHeader('posts');
		document.title = 'posts'				
	}
	else
	{
		setHeader('posts by ' + h.info 
			       + ' | <a onClick="get_pins(\''+h.info+'\');return false;" href="#">pins</a>' 
			       + ' | <a onClick="chat(\''+h.info+'\');return false;" href="#">chat</a>');
		document.title = 'posts by ' + h.info;
	}
	info1 = h.info;
	after_post_load_back();
	$('#postscroller').scrollTop(h.scrolltop);
	hide_input();
	clear()
}

function toggle_follow(uname)
{
	$.post('/toggle_follow/',
		{
			uname: uname,
			csrfmiddlewaretoken: csrf_token
		},
	function(data) 
	{
		if(data['status'] === 'followed')
		{
			$('#following_status').html('unfollow')
		}
		else if(data['status'] === 'unfollowed')
		{
			$('#following_status').html('follow')
		}
	});
}

function stream()
{
	if(loggedin !== 'yes')
	{
		show_guest_status();
		clear();
		return false;
	}
	if(typeof event !== 'undefined' && event.which == 2)
	{
		window.open('/stream/', "_blank");
	}
	else
	{
		$.get('/get_stream/',
			{

			},
		function(data) 
		{
			before_post_load();
			if(data!="")
			{
				setHeader('stream');
				$('#posts').html(data['posts']);
				$('#mode').val('stream');
				document.title = 'stream';
				after_post_load();
				$('#postscroller').scrollTop(0);
				hide_input();
			}
		});
		clear();
		return false;
	}
}

function stream_back(h)
{
	before_back();
	setHeader('stream');
	$('#posts').html(h.html);
	$('#mode').val('stream');
	document.title = 'stream';
	after_post_load_back();
	$('#postscroller').scrollTop(h.scrolltop);
	hide_input();
	clear();
}

function load_more_stream()
{
	var ids = get_posts_ids();
	$.get('/load_more_stream/',
	{
		ids: ids
	},
	function(data) 
	{
		if(data!="")
		{
			$(data['posts']).hide().appendTo('#posts').fadeIn('slow').ready(function()
			{
			});
			after_post_load();
		}
	});
	clear();
	return false;	
}

function get_posts_ids()
{
	var ids = [];

	$('.post_id').each(function(){
		ids.push($(this).val());
	})

	s = '';

	for(var i = 0; i < ids.length; i++)
	{
		s += ids[i] + ',';
	}

	return s.substring(0, s.length - 1);
}

function top_posts(uname)
{
	if(typeof event !== 'undefined' && event.which == 2)
	{
		window.open('/top/', "_blank");
	}
	else
	{
		$.get('/top_posts/',
			{
			uname: uname
			},
		function(data) 
		{
			before_post_load();
			if(data!="")
			{
				setHeader('top');
				$('#posts').html(data['posts']);
				$('#mode').val('top');
				document.title = 'top';
				after_post_load();
				$('#postscroller').scrollTop(0);
				hide_input();
			}
		});
		clear();
		return false;
	}
}

function top_posts_back(h)
{
	before_back();
	setHeader('top');
	$('#posts').html(h.html);
	$('#mode').val('top');
	document.title = 'top';
	after_post_load_back();
	$('#postscroller').scrollTop(h.scrolltop);
	hide_input();
	clear();
}

function user_on_channel(input)
{
	$.get('/user_on_channel/',
		{
		input: input
		},
	function(data) 
	{
		if(data['posts']!="")
		{
			setHeader(data['uname'] + " on " + "<a href='/" + data['cname'] + "'>" + data['cname'] + "</a>");
			$('#posts').html(data['posts']);
			$('#mode').val('useronchannel');
			document.title = data['uname'] + ' on ' + data['cname'];
			info1 = data['uname'];
			info2 = data['cname'];
			after_post_load();
			$('#postscroller').scrollTop(0);
		}
		else
		{
			dialog('nothing to see here')
		}
	});
	clear();
	return false;
}

function new_posts()
{
	if(typeof event !== 'undefined' && event.which == 2)
	{
		window.open('/new/', "_blank");
	}
	else
	{
		$.get('/new_posts/',
			{
			},
		function(data) 
		{
			before_post_load();
			if(data!="")
			{
				setHeader('new');
				$('#posts').html(data['posts']);
				$('#mode').val('new');
				document.title = 'new';
				after_post_load();
				$('#postscroller').scrollTop(0);
				hide_input();
			}
		});
		clear();
		return false;
	}
}

function new_posts_back(h)
{
	before_back();
	setHeader('new');
	$('#posts').html(h.html);
	$('#mode').val('new');
	document.title = 'new';
	after_post_load_back();
	$('#postscroller').scrollTop(h.scrolltop);
	hide_input();
	clear()
}

function load_more_new()
{
	id = $('.post_id:last').val();
	$.get('/load_more_new/',
	{
		id: id
	},
	function(data) 
	{
		if(data!="")
		{
			$(data['posts']).hide().appendTo('#posts').fadeIn('slow').ready(function()
			{
			});
			after_post_load();
		}
	});
	clear();
	return false;
}

function my_history()
{
	if(loggedin !== 'yes')
	{
		show_guest_status();
		clear();
		return false;
	}
	change_user(tehusername);
}

function next_channel_post()
{
	$.get('/next_channel_post/',
		{
		post_id: $('#channel_post:first').val()
		},
	function(data) 
	{
		$('#posts').html(data['post']);
		clear();
		after_post_load();
		return false
	});
	return false;
}

function prev_channel_post()
{
	$.get('/prev_channel_post/',
		{
		post_id: $('#channel_post:first').val()
		},
	function(data) 
	{
		$('#posts').html(data['post']);
		clear();
		after_post_load();
		return false
	});
	return false;
}

function next_channel_post_id(post_id)
{
	$.get('/next_channel_post/',
		{
		post_id: post_id
		},
	function(data) 
	{
		$('#posts').html(data['post']);
		clear();
		return false
	});
	return false;
}

function next_user_post()
{
	$.get('/next_user_post/',
		{
		post_id: $('#channel_post:first').val()
		},
	function(data) 
	{
		$('#posts').html(data['post']);
		clear();
		after_post_load();
		return false
	});
	return false;
}

function prev_user_post()
{
	$.get('/prev_user_post/',
		{
		post_id: $('#channel_post:first').val()
		},
	function(data) 
	{
		$('#posts').html(data['post']);
		clear();
		after_post_load();
		return false
	});
	return false;
}

function send_message()
{
	mode = $('#mode').val();
	content = '';
	input = $('#inputcontent').val();
	content = '@' + chattingwith + ' ' + input;
	$.post('/send_message/', { content:content, csrfmiddlewaretoken:csrf_token }, function(data)
	{
		if(data['status'] === 'ok')
		{
			if(mode === 'chat' && chattingwith === data['username'])
			{
				refresh_chat();
			}
			else if(mode === 'sent')
			{
				refresh_sent();
			}
			else
			{
				msg = "message sent to <a onClick='chat(\"" + data['username'] + "\");return false;' href=\"#\">" + data['username'] + "</a>";
				dialog(msg);
			}
		}
		else if(data['status'] === 'noreceiver')
		{
			dialog('user does not exist');
		}
		else if(data['status'] === 'sameuser')
		{
			dialog('you can\'t send messages to yourself');
		}
		else if(data['status'] === 'notallowed')
		{
			dialog('you can\'t send messages to this user');
		}
		else if(data['status'] === 'nologin')
		{
			show_guest_status();
		}
		return false;
	});
	clear();
	return false;
}

function remove_duplicate_inbox_senders()
{
	$('.chat_container').each(function()
	{
		id = $(this).children('.id').val();
		uname = $(this).children('.username').val();
		$('.chat_container').each(function()
		{
			pid = $(this).children('.id').val();
			puname = $(this).children('.username').val();
			if(uname === puname)
			{
				if(id > pid)
				{
					$(this).closest('.chat_container').remove();
				}
			}
		});
	});
}

function remove_duplicate_sent_receivers()
{
	$('.chat_container').each(function()
	{
		id = $(this).children('.id').val();
		uname = $(this).children('.receiver').val();
		$('.chat_container').each(function()
		{
			pid = $(this).children('.id').val();
			puname = $(this).children('.receiver').val();
			if(uname === puname)
			{
				if(id > pid)
				{
					$(this).closest('.chat_container').remove();
				}
			}
		});
	});
}

function remove_duplicate_chatall()
{
	$('.chat_container').each(function()
	{
		id = $(this).children('.id').val();
		uname = $(this).children('.username').val();
		runame = $(this).children('.receiver').val();
		$('.chat_container').each(function()
		{
			pid = $(this).children('.id').val();
			puname = $(this).children('.username').val();
			pruname = $(this).children('.receiver').val();
			if((uname === puname && uname != tehusername) || runame === pruname && runame != tehusername || uname === pruname && runame === puname)
			{
				if(id > pid)
				{
					$(this).closest('.chat_container').remove();
				}
			}
		});
	});
}

function refresh_channel()
{
	var id = $('.post_id:first').val();
	$.get('/refresh_channel/',
		{
			id: id,
			channel_name: document.title
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			var last_id = $('.post_id:first').val()
			$(data['posts']).prependTo('#posts');
			if(last_id !== $('.post_id:first').val())
			{
				var offset = $('#post_' + last_id).prev().offset().top
				$('#postscroller').scrollTop($('#postscroller').scrollTop() + offset);
			}
			after_post_load();
		}
	});
	return false;
}

function refresh_user()
{
	id = $('.post_id:first').val();
	$.get('/refresh_user/',
		{
			id: id,
			username: info1
		},
	function(data) 
	{
		if(data['status'] === 'ok')
		{
			$(data['posts']).prependTo('#posts');
			after_post_load();
		}
	});
	return false;
}

function refresh()
{
	mode = $('#mode').val();
	if(mode === 'channel')
	{
		//refresh_channel();
	}
	if(mode === 'user')
	{
		//refresh_user();
	}
	if(mode === 'chat')
	{
		refresh_chat();
	}
	if(mode === 'inbox')
	{
		refresh_inbox();
	}
	if(mode === 'chatall')
	{
		refresh_chatall();
	}
	if(mode === 'sent')
	{
		refresh_sent();
	}
	check_new_pms();
	check_new_alerts();
	return false;
}

function check_new_pms()
{
	$.get('/check_new_pms/',
		{
		},
	function(data) 
	{
		if(data['status'] === 'yes')
		{
			if ($('#mode').val() != 'chatall' && $('#mode').val() != 'chat')
			{
				$('#menu_chat').html("(" + data['num'] + ") &nbsp; chat");
			}
		}
		else
		{
			$('#menu_chat').html('chat');
		}
	});
	return false;
}

function check_new_alerts()
{
	$.get('/check_new_alerts/',
		{
		},
	function(data) 
	{
		if(data['status'] === 'yes')
		{
			mode = $('#mode').val();
			$('#menu_alerts').html("(" + data['num'] + ") alerts");
		}
		else
		{
			$('#menu_alerts').html('alerts');
		}
	});
	return false;
}

function UrlRecord(mode,info)
{
	this.mode = mode;
	this.info = info;
	this.html;
	this.scrollTop;
	this.channel;
}

function go_back()
{
	var state = window.history.state;

	if(state === undefined)
	{
		clear();
		return false;
	}

	mode = state.mode;

	if(mode === 'channel')
	{
		change_channel_back(state);
		return false;
	}
	if(mode === 'user')
	{
		change_user_back(state);
		return false;
	}
	if(mode === 'chat')
	{
		chat_back(state.info);
		return false;
	}
	if(mode === 'chatall')
	{
		chatall_back();
		return false;
	}
	if(mode ==='settings')
	{
		settings_back();
		return false;
	}
	if(mode ==='new')
	{
		new_posts_back(state);
		return false;
	}
	if(mode === 'post')
	{
		open_post_back(state);
		return false;
	}
	if(mode === 'top')
	{
		top_posts_back(state);
		return false;
	}
	if(mode === 'stream')
	{
		stream_back(state);
		return false;
	}
	if(mode === 'pins')
	{
		get_pins_back(state);
		return false;
	}
	if(mode === 'alerts')
	{
		alerts_back(state);
		return false;
	}

	clear();
	return false;
}

function update_url()
{
	bottomdown = false;
	mode = $('#mode').val();
	var ch = '';
	var info;
	var url;

	if(mode === 'channel')
	{
		url = document.title;
		info = document.title;
	}
	else if(mode === 'user')
	{
		url = 'user/' + info1;
		info = info1;
	}
	else if(mode === 'chat')
	{
		url = 'chat/' + info1;
		info = info1;
	}
	else if(mode === 'notes')
	{
		url = 'notes';
		info = '0';
	}
	else if(mode === 'help')
	{
		url = 'help';
		info = '0';
	}
	else if(mode === 'inbox')
	{
		url = 'inbox';
		info = '0';
	}
	else if(mode === 'sent')
	{
		url = 'sent';
		info = '0';
	}
	else if(mode === 'chatall')
	{
		url = 'chat';
		info = '0';
	}
	else if(mode === 'settings')
	{
		url = 'settings';
		info = '0';
	}
	else if(mode === 'new')
	{
		url = 'new';
		info = '0';
	}
	else if(mode === 'stream')
	{
		url = 'stream';
		info = '0';
	}
	else if(mode === 'post')
	{
		info = $('.post_id:first').val();
		url = 'post/' + info;
		ch = channel;
	}
	else if(mode === 'top')
	{
		url = 'top';
		info = '0';
	}
	else if(mode === 'pins')
	{
		url = 'pins/' + info1;
		info = info1;
	}
	else if(mode === 'useronchannel')
	{
		url = info1 + '/on/' + info2;
		info = info1 + ' on ' + info2
	}
	else if(mode === 'alerts')
	{
		url = 'alerts';
		info = 0;
	}
	else
	{
		url = '';
		mode = 'empty'
		info = '0';
	}

	if(window.history.state)
	{
		if(window.history.state.url === url)
		{
			return false;
		}
	}

	window.history.pushState({'channel': ch, 'info': info, 'mode': mode, 'url': url, 'pageTitle': 'title', 'content': 'content'}, '', '/' + url);
}

function resize_videos()
{
	$(window).off('resize');
    on_window_resize();
    var $allVideos = $("#posts iframe[src^='https://www.youtube.com'],#posts iframe[src^='http://player.vimeo.com'],#posts iframe[src^='http://www.dailymotion.com'],#posts iframe[src^='https://w.soundcloud.com']"),
        $fluidEl = $("#posts");
    $allVideos.each(function() 
    {
    		$(this).attr('height', $(this).height());
    		$(this).attr('width', $(this).width());
            $(this)
                    .data('aspectRatio', this.height / this.width)
                    .removeAttr('height')
                    .removeAttr('width');
    });
    $(window).resize(function() 
    {
            var newWidth = $fluidEl.width();
            $allVideos.each(function() 
            {
                    var $el = $(this);
                    $el
                            .width(newWidth)
                            .height(newWidth * $el.data('aspectRatio'));
            });
    }).resize();
    check_images();
}

function get_yt_id(player)
{
	for (property in player) 
	{
		for (sub in player[property]) 
		{
			if(sub === 'id') 
		  	{
		  		return(player[property][sub])
		  	}
			
		}
	} 
}

function get_yt_state(player)
{
	for (property in player) 
	{
		for (sub in player[property]) 
		{
			if(sub === 'playerState') 
		  	{
		  		return(player[property][sub])
		  	}
			
		}
	} 
}

function create_yt_players()
{
	$("#posts iframe[src^='https://www.youtube.com']").each(function()
	{
		var player = new YT.Player($(this).attr('id'), 
		{
          events: 
          {
            'onStateChange': onYouTubeStateChange
          }
        });
        var id = $(this).attr('id');
        var pid = 0;
        var has_it = false;
        for(var i=0; i < yt_players.length; i++)
		{
			pid = get_yt_id(yt_players[i])
			if(id === pid)
			{
				has_it = true;
			}
		}
		if(!has_it)
		{
        	yt_players.push(player);
		}
	});
}

function create_sc_players()
{
	$("#posts iframe[src^='https://w.soundcloud.com']").each(function()
	{
		var player = SC.Widget($(this).prop('id'))
		player.bind(SC.Widget.Events.PLAY, function() 
		{
			for(var i=0; i<sc_players.length; i++)
			{
				if(sc_players[i] !== player)
				{
					sc_players[i].pause();
				}
			}     		
	 		stop_yt_players();
			stop_vimeo_players();
			stop_audio_players();
			stop_video_players();
     	});
     	var has_it = false;
     	for(var i=0; i<sc_players.length; i++)
		{
			if(player === sc_players[i])
			{
				has_it = true;
			}
		}
		if(!has_it)
		{
        	sc_players.push(player);
		}
	})
}

function create_vimeo_players()
{
	$("#posts iframe[src^='http://player.vimeo.com']").each(function()
	{
    	var player = $f($(this)[0]);
    	player.addEvent('ready', function() 
    	{
        	player.addEvent('play', on_vimeo_play);
    	});
    	var has_it = false;
     	for(var i=0; i<vimeo_players.length; i++)
		{
			if(player === vimeo_players[i])
			{
				has_it = true;
			}
		}
		if(!has_it)
		{
        	vimeo_players.push(player);
		}
	})
}

function create_audio_players()
{
	$("#posts audio").each(function()
	{
		var player = $(this);
		player.bind('play', function()
		{
			for(var i=0; i<audio_players.length; i++)
			{
				if(player.prop('id') !== audio_players[i].prop('id'))
				{
					audio_players[i][0].pause();
				}
			}
			stop_sc_players();
			stop_vimeo_players();
			stop_yt_players();
			stop_video_players();
		});
		var has_it = false;
     	for(var i=0; i<audio_players.length; i++)
		{
			if(player.prop('id') === audio_players[i].prop('id'))
			{
				has_it = true;
			}
		}
		if(!has_it)
		{
        	audio_players.push(player);
		}
	})
}

function create_video_players()
{
	$("#posts video").each(function()
	{
		var player = $(this);
		player.bind('play', function()
		{
			for(var i=0; i<video_players.length; i++)
			{
				if(player.prop('id') !== video_players[i].prop('id'))
				{
					video_players[i][0].pause();
				}
			}
			stop_sc_players();
			stop_vimeo_players();
			stop_yt_players();
			stop_audio_players();
		});
		var has_it = false;
     	for(var i=0; i<video_players.length; i++)
		{
			if(player.prop('id') === video_players[i].prop('id'))
			{
				has_it = true;
			}
		}
		if(!has_it)
		{
        	video_players.push(player);
		}
	})
}

function on_vimeo_play(id)
{
	for(var i=0; i<vimeo_players.length; i++)
	{
		var pid = $(vimeo_players[i].element).prop('id')
		if(pid !== id)
		{
			vimeo_players[i].api('pause');
		}
	}
 	stop_yt_players();
	stop_sc_players();
	stop_audio_players();
	stop_video_players();
}

function onYouTubeStateChange(event)
{

	var id = get_yt_id(event.target);
	if(event.data == YT.PlayerState.PLAYING)
	{
		for(var i=0; i<yt_players.length; i++)
		{
			var pid = get_yt_id(yt_players[i]);
			if(pid !== id)
			{
				var state = get_yt_state(yt_players[i]);

				if(state === 1)
				{
					yt_players[i].pauseVideo();
				}
			}
		}
		stop_sc_players();
		stop_vimeo_players();
		stop_audio_players();
		stop_video_players();
	}
	if(event.data == YT.PlayerState.BUFFERING)
	{
		for(var i=0; i<yt_players.length; i++)
		{
			var pid = get_yt_id(yt_players[i]);
			if(pid !== id)
			{
				yt_players[i].pauseVideo();
			}
		}
		stop_sc_players();
		stop_vimeo_players();
		stop_audio_players();
		stop_video_players();
	}
}

function stop_yt_players()
{
	for(var i=0; i<yt_players.length; i++)
	{
		var state = get_yt_state(yt_players[i]);

		if(state === 1)
		{
			yt_players[i].pauseVideo();
		}
	} 
}

function stop_sc_players()
{
	for(var i=0; i<sc_players.length; i++)
	{
		sc_players[i].pause();
	} 
}

function stop_vimeo_players()
{
	for(var i=0; i<vimeo_players.length; i++)
	{
		vimeo_players[i].api('pause');
	}
}

function stop_audio_players()
{
	for(var i=0; i<audio_players.length; i++)
	{
		audio_players[i][0].pause();
	}
}

function stop_video_players()
{
	for(var i=0; i<video_players.length; i++)
	{
		video_players[i][0].pause();
	}
}

function delete_channel(cname)
{
    clear();
    if(cname.substring(0,1) === '#')
    {
        cname = cname.substring(1);
    }
	$.get('/delete_channel/',
		{
        cname:cname
		},
	function(data) 
	{
        change_channel(data);
        return false;
	});
    return false;        
}

function delete_post(id)
{
	var html = $('#delete_post_' + id).html();

	if(html === 'delete')
	{
		$('#delete_post_' + id).html('click again to delete');
		return;
	}

	$.post('/delete_post/',
		{
        id:id,
        csrfmiddlewaretoken: csrf_token
		},
	function(data) 
	{
		if(data.status === 'commented')
		{
			dialog("can't delete a post that has comments");
			$('#delete_post_' + id).html('delete');
		}
		else if(data.status === 'ok')
		{
			if($('#mode').val() === 'post')
			{
				my_history();
			}
			else
			{
				$('#post_' + id).fadeOut(500, function()
				{
					$(this).remove();
				});
			}
		}
	});
    return false;
}

function delete_comment(id)
{
	var html = $('#delete_comment_' + id).html();

	if(html === 'delete')
	{
		$('#delete_comment_' + id).html('click again to delete');
		return;
	}

	$.post('/delete_comment/',
		{
        id:id,
        csrfmiddlewaretoken: csrf_token
		},
	function(data) 
	{
		if(data.status === 'replied')
		{
			dialog("can't delete a comment that has replies");
			$('#delete_comment_' + id).html('delete');
		}
		else if(data.status === 'ok')
		{
			$('#comment_' + id).fadeOut(500, function()
			{
				$(this).remove();
			});
		}
	});
    return false;        
}

function count_words(input)
{
	number = 0;
	var matches = input.match(/\b/g);
    if(matches) {
        number = matches.length/2;
    }
    return number;
}

function activate_key_detection()
{
	 $(document).keyup(function(e)
	 {
		 code = (e.keyCode ? e.keyCode : e.which);
		 if (code == 27)
		 {
		 	if($('#inputcontent').val() === '' && ! $('#overlay').is(':visible'))
		 	{
		 		show_goto();
		 	}
		 	else
		 	{
				clear();
				defocus();
				hide_overlay();
		 	}
		}
		if(code == 13)
        {
        	if($('#goto_input').is(':focus'))
        	{
        		var val = $.trim($('#goto_input').val())
        		if(val !== '')
        		{
        			hide_overlay();
        			change_channel(val);
        		}
        	}
        }
	 });
	 $(document).keydown(function(e)
	 {
	 	if($('#overlay').is(':visible'))
	 	{
	 		return true;
	 	}
        code = (e.keyCode ? e.keyCode : e.which);
         //up
		 if(code == 38)
		 {
		 	if(e.ctrlKey && $('#mode').val() === 'post')
		 	{
		 		open_post($('.post_id:first').val());
		 		e.preventDefault();
		 		return false;
		 	}
		 	$('#postscroller').scrollTop($('#postscroller').scrollTop() - 100);
            e.preventDefault();
            return false;
		 }
		 //down
		 if(code == 40)
		 {
		 	if(e.ctrlKey && $('#mode').val() === 'post')
		 	{
		 		show_last_comments();
		 		e.preventDefault();
		 		return false;
		 	}
		 	$('#postscroller').scrollTop($('#postscroller').scrollTop() + 100);
            e.preventDefault();
            return false;
		 }
        if($('#inputcontent').is(':focus'))
        {
			if($('#inputcontent').val() != '')
			{
				if (code == 13)
				{
					var value = $('#inputcontent').val();
					if(value.substring(0,7) === 'global:')
					{
                        if($.trim(value.substring(7)) === '')
                        {
                            clear();
                            return false;
                        }
						send_global_pm();
					}
					else if(value === 'whoami')
					{
						whoami();
					}
					else if(value.substring(0,5) === 'seen ')
					{
						var username = $.trim($('#inputcontent').val().substring(5));
                        if(username === '')
                        {
                            clear();
                            return false;
                        }
                        seen(username);
					}
					else if(value.substring(0,7) === 'notes ')
					{
                        if($.trim(value.substring(7)) === '')
                        {
                            notes();
                            return false;
                        }
                        note(value.substring(7));
					}
					else if(value.substring(0,9) === '!silence ')
					{
                        if($.trim(value.substring(9)) === '')
                        {
                            return false;
                        }
                        silence(value.substring(9));
					}
					else if(value.substring(0,11) === 'unsilence ')
					{
                        if($.trim(value.substring(11)) === "")
                        {
                            return false;
                        }
                        unsilence(value.substring(11));
					}
					else if(value.substring(0,6) === '!note ')
					{
                        note(value.substring(6));
					}
					else if(value.substring(0,6) === '!calc ')
					{
                        if($.trim(value.substring(6)) === '')
                        {
                            clear();
                            return false;
                        }
                        var num = 'nope';
                        try{
                            num = eval(value.substring(6));
                        }
                        catch(err)
                        {
                        }
                        if(num!='nope')
                        {
                            calculator(value.substring(6),num);
                            return false;
                        }
                        else{
                            clear();
                            return false;
                        }
					}
					else if(value.toLowerCase() === 'delchannel')
					{
                        delete_channel(document.title);
					}
					else if(value.toLowerCase() === 'delpost' && $('#mode').val() === 'post')
					{
                        delete_post();
                        clear();
					}
					else if(value.toLowerCase() === '!url')
					{
						show_url();
					}
					else if(value.toLowerCase() === '!silenced')
					{
						silenced();
					}
					else if(value.substring(0,6) === 'reply:')
					{
						reply_to_comment(value.substring(6), reply_to_id, true);
					}
					else if(value.toLowerCase() === '!tab')
					{
						open_tab();
					}
					else if(value.toLowerCase() === '!close')
					{
						close_tab();
					}
					else if(value.toLowerCase() === '!login')
					{
						login();
					}
					else if(value.toLowerCase() === '!logout')
					{
						login();
					}
					else if(value.toLowerCase() === '!notes')
					{
						notes();
					}
					else if(value.toLowerCase() === '!note')
					{
						notes();
					}
					else if(value.toLowerCase() === '!settings')
					{
						settings();
					}
					else if(value.toLowerCase() === '!chat')
					{
						chatall();
					}
					else if(value.toLowerCase() === '!inbox')
					{
						inbox();
					}
					else if(value.toLowerCase() === '!sent')
					{
						sent();
					}
					else if(value.toLowerCase() === '!back')
					{
						go_back();
					}
					else if(value.toLowerCase() === '!refresh')
					{
						refresh();
						clear();
					}
					else if(value.toLowerCase() === '!posts')
					{
						my_history();
						clear();
					}
					else if(value.toLowerCase() === '!new')
					{
						new_posts();
						clear();
					}
					else if(value.toLowerCase() === '!top')
					{
						top_posts();
						clear();
					}
					else if(value.toLowerCase() === '!alerts')
					{
						alerts();
						clear();
					}
					else if(value.toLowerCase() === '!pin')
					{
						if($('#mode').val() === 'post')
						{
							id = $('.post_id').val();
							pin(id);
							clear();
						}
						clear();
						return false;
					}
					else if(value.toLowerCase() === '!pins')
					{
						get_pins(tehusername);
						clear();
					}							
					else if($('#mode').val() === 'channel')
					{
						post_to_channel(value);
					}
					else if($('#mode').val() === 'post')
					{
                        post_comment(value);
					}
					else if($('#mode').val() === 'chat')
					{
						send_message();
					}
					else if($('#mode').val() === 'notes')
					{
						note(value);
					}
					clear();
					e.preventDefault();
				}
			}
		}
		if($('.commentinput').is(':focus'))
		{
			if (code == 13)
			{

				var content = $(document.activeElement).val()
				if(content !== '')
				{
					var post_id = $(document.activeElement).attr('id').replace('ci_', '')
					if(content.substring(0,6) === 'reply:')
					{
						reply_to_comment(content.substring(6), reply_to_id, false);
					}
					else
					{
						post_inline_comment(post_id, content)
					}
					$(document.activeElement).val('')
				}
			}
		}
		var inp = String.fromCharCode(code);
		if(!e.ctrlKey && $('#mode').val() !== 'settings' && ! $('.commentinput').is(':focus'))
		{
			$('#inputcontent').focus();
		}
		else
		{
			//letter v
			if(code == 86 && $('#mode').val() !== 'settings')
			{
				$('#inputcontent').focus();
			}
			// down
			if(code == 40)
			{
				e.preventDefault();
				return false;
			}
			// up
			if(code == 38)
			{
				e.preventDefault();
				return false;
			}
		}
		if($('#inputcontent').val() === '' && ! $('.alert_reply_input').is(':focus') && ! $('.commentinput').is(':focus'))
		{
			//spacebar
			if(code == 32)
			{
				if(e.ctrlKey)
				{
					random_channel();
				}
				else
				{
					random_post();
				}
				e.preventDefault();
			}
			if(code == 37)
			{
				e.preventDefault();
			}
			if(code == 39)
			{
				e.preventDefault();
			}
					
		}
	});
}

function activate_scroller()
{
	$('#postscroller').niceScroll(
	{
		zindex:9999,
		mousescrollstep:750,
		autohidemode:false,
		enablemousewheel:false,
		enablekeyboard:false,
		cursorminheight: 80,
		cursorwidth: 5,
		cursorcolor: "#bababa",
		cursorborder: "0px solid #fff",
		railoffset: {top:0,left:26},
		horizrailenabled: false,
	});
	$('#postscroller').scroll(function()
	{
		$('#postscroller').niceScroll().resize();
		if($('#postscroller').getNiceScroll()[0].cursorfreezed)
		{
			$('#postscroller').getNiceScroll()[0].cursorfreezed = false;
		}
    	if (($('#postscroller').outerHeight() + 10) >= ($('#postscroller').get(0).scrollHeight - $('#postscroller').scrollTop()))
    	{
    		if(!bottomdown)
    		{
       			load_more();
       			bottomdown = true;
       			bottomtimer();
    		}
       	}
    	if(($('#postscroller').scrollTop()) == 0)
    	{
    		if($('#mode').val() === 'post')
    		{
       			show_older_comments();
    		}
       	}
	});
}

function resize_page()
{
	var window_height = $(window).height();
	var header_height = $('#header').outerHeight();
	var posts_padding = 25;
	var input_height = 0;
	var input_border = 0;
	if($('#inputcontent').is(':visible'))
	{
		input_height = $('#inputcontent').outerHeight();
		input_border = 2;
	}
	var height = window_height - header_height - input_height - posts_padding - input_border;
	$('#colmask').css('height', window_height);
	$('#postscroller').css('height', height);
}

function on_window_resize()
{
	$(window).resize(function()
	{
		resize_page();
	})
}

function hide_pm(pm,id)
{
	pm.fadeOut("normal", function() 
	{
        $(this).remove();
    });
	$.get('/hide_pm/',
		{
		id: id
		},
	function(data) 
	{
		return false
	});
	return false;
}

function show_input(ph)
{
	$('#inputcontent').css('display', 'block')
	$('#inputcontent').attr('placeholder', ph)
	resize_page();
}

function hide_input()
{
	$('#inputcontent').css('display', 'none');
	resize_page();
}

function initial_settings()
{
	if(loggedin === 'yes')
	{
		if(theme_background === '' || theme_background === "0")
		{
			theme_background = $('body').css('background-color');
			theme_text = $('body').css('color');
			theme_link = $('a').css('color');
			theme_input_background = $('#inputcontent').css('background-color');
			theme_input_text = $('#inputcontent').css('color');
			theme_input_border = $('#inputcontent').css('border-top-color');
			theme_input_placeholder = "#bbbbbb";
			theme_scroll_background = "#bababa";
		}
	}
	else
	{
		theme_background = '';
		theme_text = '';
		theme_link = '';
		theme_input_background = '';
		theme_input_text = '';
		theme_input_border = '';
		theme_input_placeholder = '';
		theme_scroll_background = '';
	}
}

function activate_refresh()
{
	setInterval(function()
	{
		refresh();
	},30000);
}

function activate_mousewheel()
{
	$(document).bind('touchmove', function (e)
	{
		var touch = e.originalEvent.touches[0] || e.originalEvent.changedTouches[0];
		var currentY = touch.clientY;
		if(currentY > lastY)
		{
			$('#postscroller').scrollTop($('#postscroller').scrollTop() - 30);
		}
		else
		{
			$('#postscroller').scrollTop($('#postscroller').scrollTop() + 30);
		}
		e.preventDefault();
		lastY = currentY;
	});
	$(document).bind('mousewheel', function(event, delta, deltaX, deltaY) 
	{
		if(delta < 0)
		{
			$('#postscroller').scrollTop($('#postscroller').scrollTop() + 60);
		}
		else
		{
			$('#postscroller').scrollTop($('#postscroller').scrollTop() - 60);
		}
	});
}

function add_placeholder_style()
{
	var defaultColor = 'BBBBBB';
	var styleContent = 'input:-moz-placeholder {color: #' + defaultColor + ';} input::-moz-placeholder {color: #' + defaultColor + ';} input::-webkit-input-placeholder {color: #' + defaultColor + ';} input:-ms-input-placeholder {color: #' + defaultColor + ';}';
	var styleBlock = '<style id="placeholder-style">' + styleContent + '</style>';
	$('head').append(styleBlock);
}

function activate_history_listener()
{
	window.addEventListener('popstate', function(e) 
	{
		if(e.state !== null)
		{
			go_back();
		}
	});
}

function init(mode, info)
{
	$.ajaxSetup({ cache: false });
	add_placeholder_style()
	resize_page();
	activate_scroller();
	on_window_resize();
    channel_listener();
    start_left_menu();
    start_right_menu();
    initial_settings();
    if(mode === 'channel')
    {
    	change_channel(info);
    }
    else if(mode === 'user')
    {
    	change_user(info);
    }
    else if(mode === 'chat')
    {
    	chat(info);
    }
    else if(mode === 'new')
    {
    	new_posts();
    }
    else if(mode === 'notes')
    {
    	notes();
    }
    else if(mode === 'help')
    {
    	get_help();
    }
    else if(mode === 'chatall')
    {
    	chatall();
    }
    else if(mode === 'inbox')
    {
    	inbox();
    }
    else if(mode === 'sent')
    {
    	sent();
    }
    else if(mode === 'settings') 
    {
    	settings();
    }
    else if(mode === 'post')
    {
    	open_post(info);
    }
    else if(mode === 'top')
    {
    	top_posts(info);
    }
    else if(mode === 'pins')
    {
    	get_pins(info);
    }
    else if(mode === 'useronchannel')
    {
    	user_on_channel(info);
    }
    else if(mode === 'alerts')
    {
    	alerts();
    }
    else if(mode === 'random')
    {
    	random_post();
    }
    else if(mode === 'stream')
    {
    	stream();
    }
    else
    {
    	new_posts();
    }
	activate_key_detection();
    activate_timeago();
    bottomdown = false;
    activate_refresh();
    activate_mousewheel();
    check_new_pms();
    check_new_alerts();
    activate_history_listener();
}
