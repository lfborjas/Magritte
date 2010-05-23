$(function(){
	//bind some keys to the document ready:
	//based on http://seriouscoding.com/keyboard-navigation-with-javascript-and-jquer
	$(document).keydown(function(event){
		var key = event.keyCode || event.which;
		var element="";		
		if(event.target.type !== 'text' && event.target.type !== 'select'){
			//LEFT = graph
			if(key=== 37){
				element = '#user-profile';
			}
			//UP=tools
			else if(key===38){
				element = '#tools';
			}
			//RIGHT=simulation ranked
			else if(key===39){
				element = "#simulation-ranked";
			}
			//DOWN = simulation unranked
			else if(key===40){
				element = "#simulation-unranked";
			}
			$(element).effect('highlight', {}, 1000);
			
		}//if not a text or a select
	}); // end of keybindings
	
	//get users of an app:
	$('#id_appId').change(function(e){
		if($(this).val()){
			$.get('/prototype/getUsers/',
					{appId: $(this).val()},
					function(data){
						$.each(data, function(index, user){
							$('#id_appUser').append('<option value="'+user.k+'">'+user.val+'</option>');
						});
						$('#tools-submit, #simulation-submit').removeAttr('disabled');
					},
					'json'
			);
		}else{
			$('#tools-submit, #simulation-submit').attr('disabled','disabled');
			$('#id_appUser').empty();
		}
	});
	
	//set the appropiate profile
	$('#tools-form').submit(function(e){
		e.preventDefault();
		$.getJSON('/api/demo/setProfile/',
				$('#tools-form').serialize(),
				function(data){
					//alert(data.graph);
					$('.user-info').text("Perfil actual: "+ $('#id_appUser :selected').text().replace( /^\s+|\s+$/g, '')
										 +", usuario de "+$('#id_appId :selected').text().replace( /^\s+|\s+$/g, ''))
					$('#user-profile-graph').attr('src', data.graph);
					$('#user-profile-graph-thumb').attr('href', data.graph);
				});
	});
	
	//simulate a query:
	$('#simulation-form').submit(function(e){
		e.preventDefault();
		$.getJSON('/search/',
				$('#simulation-form').serialize(),
				function(data){
					$('#simulation-unranked').prepend('<h4 class="sim-results">Sin re-ordenar</h4>');
					$.each(data.results, function(index, unranked){						
						$('#unranked-results').append('<li><a target="_blank" href="'+unranked.url+'">'+unranked.title+'</a></li>');
					});
					$('#simulation-ranked').prepend('<h4 class="sim-results">Re-ordenando</h4>');
					$.each(data.reranked, function(index, ranked){
						$('#ranked-results').append('<li><a target="_blank" href="'+ranked.url+'">'+ranked.title+'</a></li>');
					});
				}
		);
	});
});
