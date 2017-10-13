/*

CollapsibleLists.js

An object allowing lists to dynamically expand and collapse

Created by Stephen Morley - http://code.stephenmorley.org/ - and released under
the terms of the CC0 1.0 Universal legal code:

http://creativecommons.org/publicdomain/zero/1.0/legalcode

*/

const CollapsibleLists = (function(){

  // Makes all lists with the class 'collapsibleList' collapsible. The
  // parameter is:
  //
  // doNotRecurse - true if sub-lists should not be made collapsible
  function apply(doNotRecurse){

    [].forEach.call(document.getElementsByTagName('ul'), node => {

      if (node.classList.contains('collapsibleList')){

        applyTo(node, true);

        if (!doNotRecurse){

          [].forEach.call(node.getElementsByTagName('ul'), subnode => {
            subnode.classList.add('collapsibleList')
          });

        }

      }

    })

  }

  // Makes the specified list collapsible. The parameters are:
  //
  // node         - the list element
  // doNotRecurse - true if sub-lists should not be made collapsible
  function applyTo(node, doNotRecurse){

    [].forEach.call(node.getElementsByTagName('li'), li => {

      if (!doNotRecurse || node === li.parentNode){

        li.style.userSelect       = 'none';
        li.style.MozUserSelect    = 'none';
        li.style.msUserSelect     = 'none';
        li.style.WebkitUserSelect = 'none';

        li.addEventListener('click', handleClick.bind(null, li));

        toggle(li);

      }

    });

  }

  // Handles a click. The parameter is:
  //
  // node - the node for which clicks are being handled
  function handleClick(node, e){

    let li = e.target;
    while (li.nodeName !== 'LI'){
      li = li.parentNode;
    }

    if (li === node){
      toggle(node);
    }

  }

  // Opens or closes the unordered list elements directly within the
  // specified node. The parameter is:
  //
  // node - the node containing the unordered list elements
  function toggle(node){

    const open = node.classList.contains('collapsibleListClosed');
    const uls  = node.getElementsByTagName('ul');

    [].forEach.call(uls, ul => {

      let li = ul;
      while (li.nodeName !== 'LI'){
        li = li.parentNode;
      }

      if (li === node){
        ul.style.display = (open ? 'block' : 'none');
      }

    });

    node.classList.remove('collapsibleListOpen');
    node.classList.remove('collapsibleListClosed');

    if (uls.length > 0){
      node.classList.add('collapsibleList' + (open ? 'Open' : 'Closed'));
    }

  }

  return {apply, applyTo};

})();
