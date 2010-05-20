/*Namespace for handling recommendations
 * @author: lfborjas
 * 
 * Notes: the token for the default app is 0a0c8647baf451dc081429aa9815d476
 */
if(!window.RECOMMENDER){
	var _service_root="http://localhost:8000/";
	RECOMMENDER = {
			/*The urls to diverse service calls*/
			//_service_root: "http://lebrixen.com",
			//_service_root: "http://localhost:8000/",
			//initial call url:
			_init_call: _service_root+"api/startSession/?callback=?",
			_get_recommendations_call: _service_root+"api/getRecommendations/?callback=?",
			_final_call: _service_root+"api/endSession/?callback=?",
			
			/*Internal data*/
			_lastContext: "",
			_lastLength: 0,
			_triggerWords: 2,
			_wordsDiff: 0,
			_diff: 0,
			
			_defaults: {
					appId: '0a0c8647baf451dc081429aa9815d476',
					appUser: 'testUser',
					content: '#id_content',
					lang: 'en',
			  },
			  
			_options: {},
			
			/*Interface data*/
			
			/*Web service call functions*/
			
			/**Send the context and the documents to the service to evolve the profile*/
			endSession: function(event){
				/*This is asynchronous, so the server might not find the caller,
				 * dunno how to solve it (a jsonp CAN'T be synchronous, so it's
				 * no case setting async to false in $.ajax*/
				$.get(RECOMMENDER._final_call,
						{context: $('#terms').val()},
						'jsonp'
						);
				return false;
			},//end of the end session definition
			
			/**Set the options and make the initial call*/			
			init: function(options){
				//make the plugin's options a deep copy of the union of the defaults and options				
				$.extend(true, RECOMMENDER._options, RECOMMENDER._defaults, options);
				
				//Append the recommender bar to the host's body and bind it's events
				$.getJSON(RECOMMENDER._init_call,
						{appId: RECOMMENDER._options.appId, appUser: RECOMMENDER._options.appUser},
						function(data){
							$('body').append(data.recommender_bar);
							//to toggle the bar
							$(".trigger").click(function(){
								$(".panel").toggle("fast");
								//$(this).toggleClass("active");
								return false;
							});
				});

				//Set the host's components events
				$('#id_content').keyup(RECOMMENDER.detectContextChange);				   
				
				//Call the user trigger or default to the window unloading
				if(!RECOMMENDER._options.trigger){
					$(window).unload(RECOMMENDER.endSession);
				}else{
					$(RECOMMENDER._options.trigger).click(RECOMMENDER.endSession);
				}
				
				//return false;
			},//end of init definition
			
			/**Determine when to make new recommendations*/	
			detectContextChange: function(e){
				   if(e.which == 32){ RECOMMENDER._diff ++;}
					
				   //primitive context change sensibility: lexical comparison...
				   //start detecting the context after the initial words treshold
				   wordcount = $('#id_content').val().split(' ').length;
				   if(wordcount >= RECOMMENDER._triggerWords && RECOMMENDER._diff >= RECOMMENDER._wordsDiff){
					   if(wordcount != RECOMMENDER._lastLength && $('#id_content').val() != RECOMMENDER._lastContext){			   
						   RECOMMENDER._lastContext = $('#id_content').val();
						   RECOMMENDER._lastLength = wordcount;
						   RECOMMENDER._diff = 0;
						   //call the extraction method:
						   RECOMMENDER.doQuery();
					   }
				   }					
			},//end of detectContextChange definition
			
			/**Get the actual recommendations*/
			doQuery: function(){
				$.post(RECOMMENDER._get_recommendations_call,
						{content: $(RECOMMENDER._options.content).val(), lang : RECOMMENDER._options.lang},
						function(data){
							$('#docs-container').html("");
							if(!data.results){
								$('#docs-title').hide();
							}else{
								$('#terms-title').show();						
								$('#terms').val(data.terms);					
								$('#terms').effect('highlight');
								$('#docs-title').show().text("Documentos Recomendados ("+data.results.length+")");
							}
							$.each(data.results, function(index, hit){					
								$('#docs-container').append('<div class="result" id="doc_'+hit.id+'">'+
												   '<a target="_blank" href="'+hit.url+'"><strong>'+hit.title+'</strong></a>'+									    
												   '<p>'+hit.summary+'</p>'+									   
												 '</li>');
								
							});
							$('#docs').effect('highlight');
							if(!$('.trigger').hasClass('active'))
								$('.trigger').addClass("active");
							$('.trigger').effect("pulsate", {times:5}, 2000);
						},
						'jsonp');
			},//end of doQuery definition
			
	}//end of namespace RECOMMENDER
}



