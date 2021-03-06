export function revealCutCard(card, dealer, isJoker) {
  let cutCardImage = $('<img/>', {
    id: card,
    class: 'cut-card',
    src: '/static/img/cards/' + card
  });
  $('#deck').hide();
  $('.deck-container').append(cutCardImage);
  addPlayPile();
  $('.count-text').show();
  $('#play-total').show().text(0);

  if (isJoker) {
    if (dealer === sessionStorage.getItem('nickname')) {
      $('#joker-selector').modal({
        backdrop: 'static',
        keyboard: false
      });
    }
  }
}

function addPlayPile() {
  // append play pile to main players play area and set cards to be played
  let playPile = $('<div/>', {
    class: 'play-pile col-2 justify-content-center',
  });
  $('.player-play-area').prepend(playPile);
  let playerCards = $('.player-cards').find('.card');
  $.each(playerCards, function(index, playerCard) {
    $(playerCard).addClass('to-be-played');
  });
  $('.player-cards').removeClass('col-12').addClass('col-10').css({'text-align': 'center', 'margin': '0'});

  // append play pile to opponents play area and set cards to be played
  let opponents = $('.opponent');
  $.each(opponents, function(index, opponent) {
    let opponentPlayPile = $('<div/>', {
      class: 'play-pile col-2 justify-content-center',
    });
    $(opponent).find('.opponent-play-area').prepend(opponentPlayPile);
  });
  let opponentCards = $('.opponent-card');
  $.each(opponentCards, function(index, opponentCard) {
    $(opponentCard).addClass('to-be-played');
  });
}

export function showCutJoker(player, replacementId) {
  $('.cut-card').attr("src", '/static/img/cards/' + replacementId);
}