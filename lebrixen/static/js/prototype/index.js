var lastContext = "";
var lastLength = 0;
var triggerWords = 5;
var spaceBarCode = 32;
//var words = 0;

/*Be as lazy as possible in context detection, but determine it efectively*/
function detectContextChange(e){
	   /*if(e.which == spaceBarCode){ words ++;}*/
	
	   //primitive context change sensibility: lexical comparison...
	   //start detecting the context after the initial words treshold
	   wordcount = $('#id_content').val().split(' ').length;
	   if(wordcount >= triggerWords){
		   if(wordcount != lastLength && $('#id_content').val() != lastContext){			   
			   lastContext = $('#id_content').val();
			   lastLength = wordcount;
			   //call the extraction method:
			   
		   }
	   }
}

$(document).ready(function() {
	/*When the words in the content area reach a treshold, call the extract terms event*/
   $('#id_content').keyup(detectContextChange);
});