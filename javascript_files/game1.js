var container = document.querySelector(".text");
console.log('rist');
console.log(container);

var speeds = {
   pause: 500, //Higher number = longer delay
   slow: 120,
   normal: 90,
   fast: 40,
   superFast: 10
};

var text0 = [
   { speed: speeds.slow, string: " Hello there!" },
   { speed: speeds.pause, string: "", pause: true },
   { speed: speeds.normal, string: "I am here to help you escape Alcatraz.", pause: true }
];

var text1 = [
    { speed: speeds.slow, string: "This is no ordinary escape route." },
   { speed: speeds.pause, string: "", pause: true },
   { speed: speeds.normal, string: "You must move as a group and use your wits to escape.", pause: true}
];

var text2 = [
   {speed: speeds.normal, string: "Your first test is with another prisoner."}
];

var text3 = [
   {speed: speeds.normal, string: "You can either cooperate with the prisoner,"},
   {speed: speeds.normal, string: "Or you can cheat the prisoner, and tell the guard."}
];

var text4 = [
   {speed: speeds.normal, string: "Work with your friend(s) and decide on the best course of action."},
];


let obj = {temp: -1};

function revealOneCharacter(list) {
   var next = list.splice(0, 1)[0];
   next.span.classList.add("revealed");
   next.classes.forEach((c) => {
      next.span.classList.add(c);
   });
   var delay = next.isSpace && !next.pause ? 0 : next.delayAfter;
   // if(list.length === 11){
   //    console.log('in the else if: remove');
   //    removeAllChildNodes(container);
   // }
   if (list.length > 0) {
      setTimeout(function () {
         revealOneCharacter(list);
      }, delay);
   }
   else{
      console.log("removing");
      for (let i = container.children.length - 1; i >= 0; i--) {
         if (container.children[i].nodeName === 'SPAN') {
            container.children[i].classList.remove("revealed");
            container.children[i].classList.add("hidden");
         }
      }
      if (proxyObj.temp < 0){
         proxyObj.temp = proxyObj.temp + 1;
      }
      else{
         window.location.href = 'http://' + document.domain + ':' + location.port + '/game1vote';
      }
   }

}

function removeAllChildNodes(parent) {
   console.log('removing');
   for (let i = parent.children.length - 1; i >= 0; i--) {
      if (parent.children[i].nodeName === 'SPAN') {
         parent.removeChild(parent.children[i]);
      }
   }
}

var characters = []; //This must be outside, not sure, but now more than half of the character are being revealed.

const proxyObj = new Proxy(obj, {
   set: function(target, prop, value){
      target[prop] = value;
      console.log("inside set function");

      exec(value);


   }
});


function exec(newValue){

   console.log(newValue);
   temp = newValue;
   if (temp === 0) {
      var textLines;
      console.log("STRING NUMBER: ");
      console.log(temp);
   }



   // container.classList.add(temp.toString());

   console.log("container");
   console.log(container.classList);

   switch(temp){
      case 0:
         textLines = text0;
         break;
      // case 1:
      //    textLines = text1;
      //    break;
      // case 2:
      //    textLines = text2;
      //    break;
      // case 3:
      //    textLines = text3;
      //    break;
      // case 4:
      //    textLines = text4;
      //    break;
   }
   // if (temp === 0) {
   //    textLines = text1;
   // } else {
   //    textLines = text2;
   // }

   textLines.forEach((line, index) => {

      if (index < textLines.length - 1) {
         line.string += " "; //Add a space between lines
      }

      line.string.split("").forEach((character) => {
         var span = document.createElement("span");
         span.textContent = character;
         container.appendChild(span);
         characters.push({
            span: span,
            isSpace: character === " " && !line.pause,
            delayAfter: line.speed,
            classes: line.classes || []
         });
      });
   });

   // setTimeout(() => {
   //    revealOneCharacter(characters);
   // }, 600);
   revealOneCharacter(characters);



}

proxyObj.temp = proxyObj.temp + 1;
//Kick it off





