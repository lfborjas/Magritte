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
			_init_call: _service_root+"api/getWidget/?callback=?",
			_get_recommendations_call: _service_root+"api/getRecommendations/?callback=?",
			_final_call: _service_root+"api/updateProfile/?callback=?",
			
			/*Internal data*/
			_lastContext: "",
			_lastLength: 0,
			_triggerWords: 2,
			_wordsDiff: 0,
			_diff: 0,
			_feedback: [],
			
			_defaults: {
					appId: '0a0c8647baf451dc081429aa9815d476',
					appUser: 'testUser',
					content: '#id_content',
					lang: 'en',
					data: {
						submit: null,  //the element that triggers the host's form submission, must NOT have an event handler
						form: null, //the form where the host's data lives
					},					
					feedback: {
						mode: "follow", //if select, the docs will be jquery selectables and appended to the container
						container: null,//where to send the selected, only valid if mode is 'select'
						element: "<li></li>"//how to append to the container, defaults to list element
					}			 
					
			  },
			  
			_options: {},
			
			/*Interface data*/
			
			/*Web service call functions*/
			/**Give feedback: depending on the mode set. The element must always be jquery of a '.result'*/
			giveFeedback: function(element){
				//let's assume that if select, the event target is the entire result:
				if(RECOMMENDER._options.feedback.mode == "select"){
					$(RECOMMENDER._options.feedback.container).append(RECOMMENDER._options.feedback.element);
					$(RECOMMENDER._options.feedback.container).children(':last')
					                                          .append(element.parent().find('a.lebrixen-resource').clone());					
				}
				//if follow, only add it				
				RECOMMENDER._feedback.push(parseInt(element.attr('id').split('_').pop()));
			},
			
			_bind_feedback: function(element){
				if(RECOMMENDER._options.feedback.mode == "select"){					
					$(element).find('.lebrixen-feedback-action').show().click(function(event){
						event.preventDefault();
						RECOMMENDER.giveFeedback($(event.target));						
					});										
				}else{
					$(element+' a.lebrixen-resource').click(function(event){						
						event.preventDefault();						
						RECOMMENDER.giveFeedback($(event.target).parent().parent());
						window.open($(event.target).parent().attr('href'), '_blank');
					});					
				}
			},
			
			/**Send the context and the documents to the service to evolve the profile*/
			endSession: function(event){
				/*This is asynchronous, so the server might not find the caller,
				 * dunno how to solve it (a jsonp CAN'T be synchronous, so it's
				 * no case setting async to false in $.ajax*/
				$.getJSON(RECOMMENDER._final_call,
						$.param({context: $('#terms').val(), docs: RECOMMENDER._feedback,
							lang: RECOMMENDER._options.lang, t: true}, true)						
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
							//to toggle the bar open
							$(".trigger").click(function(){
								$(".panel").toggle("fast");
								$(this).hide();
								//$(this).toggleClass("active");
								return false;
							});
							//to close the bar:
							$("#lebrixen-hide-panel").click(function(e){
								e.preventDefault();
								$(".panel").toggle("fast");
								$('.trigger').show();
								return false;
							})
							//set the slider:
							$('#lebrixen-average-rel-slider').slider({
								disabled: true,
								range: "min",
								min: 0,
								change: function(event, ui){
									//var v = parseInt(ui.value);
									v = ui.value;
									$('#lebrixen-average-rel-title').text("Relevancia promedio:"+v+"%");
									if(v < 30){
										$('#lebrixen-average-rel-slider .ui-widget-header').css('background', '#ff3333');
									}else if(v >= 30 && v < 60){
										$('#lebrixen-average-rel-slider .ui-widget-header').css('background', '#ffff33');
									}else{
										$('#lebrixen-average-rel-slider .ui-widget-header').css('background', '#66ff00');
									}
								}//end of slider change
							});//end of slider setting
							//BUT hide it till is time to show it!
							$("#lebrixen-average-rel-slider").hide();
												
							
				});

				//Set the host's components events
				$('#id_content').keyup(RECOMMENDER.detectContextChange);				   
				
				//Call the user trigger or default to the window unloading
				if(!RECOMMENDER._options.data.submit){
					$(window).unload(RECOMMENDER.endSession);
				}else{
					$(RECOMMENDER._options.data.submit).click(function(event){
							//disable the button, for those impatient users that over-submit stuff
							$(event.target).attr('disabled', 'disabled');
							event.preventDefault();
							$.getJSON(RECOMMENDER._final_call,
									//cf: http://api.jquery.com/jQuery.param/
									$.param({context: $('#terms').val(),
										     docs: RECOMMENDER._feedback,
										     lang: RECOMMENDER._options.lang, t:true}, true),
									function(){
										//force sync: only submit when the function returns
										$(RECOMMENDER._options.data.form).submit();
										return false;
									}//end of final call callback
							);
							
					});//end of data_submit click binding
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
							var cnt = 0;
							$('#docs-container').html("");
							if(!data.results){
								$('#docs-title').hide();
							}else{
								$('#terms-title').show();						
								$('#terms').val(data.terms);					
								$('#terms').effect('highlight');
								$('#docs-title').show().text("Recomendaciones ("+data.results.length+")");
							}							
							var smry=[];
							$.each(data.results, function(index, hit){
								smry = hit.summary.split(' ');
								$('#docs-container').append('<div class="result" id="doc_'+hit.id+'">'+
												   '<a class="lebrixen-feedback-action" id="fdbk_'+hit.id+
												   '" title="Add to resources" href="#" style="display:none;">Add</a>'+												   
												   '<div id="content_'+hit.id+'" class="lebrixen-result-content">'+
												   '<a class="lebrixen-resource" target="_blank" href="'+hit.url+'"><strong>'+
												   hit.title+'</strong></a>'+
												   '<p><span class="summary_hint">'+smry.slice(0, 10).join(' ')+
												   '...</span><span class="summary_body" style="display:none;">'+
												   smry.slice(11).join(' ')+'<span></p></div>'+
												 '</div>');
								cnt += hit.percent;
							});					
							
							//set the slider:
							$("#lebrixen-average-rel-slider").show();
							if(data.results){
								//behavior for the results:
								$('.result').hover(function(e){
									$(e.target).find('.summary_body').show();
								}, function(e){
									$(e.target).find('.summary_body').hide();
								});
								RECOMMENDER._bind_feedback('.result');
								$("#lebrixen-average-rel-slider").slider('value', cnt/data.results.length);
							}else{
								$("#lebrixen-average-rel-slider").slider('value', cnt);
							}
							$('#docs').effect('highlight');
							if($('.trigger').is(':visible')){
								if(!$('.trigger').hasClass('active'))
									$('.trigger').addClass("active");
								$('.trigger').effect("pulsate", {times:5}, 1000);
							}
						},
						'jsonp');
			},//end of doQuery definition
			
	}//end of namespace RECOMMENDER
}



