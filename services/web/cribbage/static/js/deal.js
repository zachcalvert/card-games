export function deal(msg) {
  $.each(msg.hands, function(player, cards) {
    if (player === sessionStorage.getItem('nickname')) {
        let card_ids = []
        $.each(cards, function(index, card) {
          let cardImage = $('<img/>', {
            id: card['id'],
            class: 'playerCard',
            src: '/static/img' + card['image']
          });
          let cardListItem = $('<li/>', {
            class: 'list-group-item',
          });
          cardListItem.append(cardImage)
          $('#' + player + '-cards').append(cardListItem);
          card_ids.push(card['id'])
        });
        sessionStorage.setItem('card_ids', JSON.stringify(card_ids))
    } else {
      $.each(cards, function(index, card) {
        let cardImage = $('<img/>', {
          id: card['id'],
          class: 'opponentCard',
          src: '/static/img/cards/facedown.png'
        });
        $('#' + player + '-cards').append(cardImage);
      });
    }
  });
};