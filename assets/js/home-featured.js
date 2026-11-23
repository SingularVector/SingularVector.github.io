(function ()
{
    'use strict';

    var grid = document.getElementById('workbench-selection');
    var template = document.getElementById('workbench-pool');

    if (!grid || !template || !template.content)
    {
        return;
    }

    var candidates = Array.from(template.content.querySelectorAll('.home-feature'));

    if (candidates.length === 0)
    {
        return;
    }

    // UTC gives every visitor the same selection for a calendar day. There is
    // no visitor identifier, storage, network request or per-refresh randomness.
    var day = Math.floor(Date.now() / 86400000);
    var topics = [];
    var groups = new Map();

    candidates.forEach(function (card)
    {
        var topic = card.dataset.featureTopic;

        if (!groups.has(topic))
        {
            topics.push(topic);
            groups.set(topic, []);
        }

        groups.get(topic).push(card);
    });

    var selected = [];
    var topicStart = day % topics.length;

    // Rotate the topics daily, then advance each topic's article after a full
    // topic cycle. This lets smaller pools participate without starving them.
    var articleTurn = Math.floor(day / topics.length);

    for (var offset = 0; offset < Math.min(3, topics.length); offset += 1)
    {
        var topic = topics[(topicStart + offset) % topics.length];
        var articles = groups.get(topic);

        selected.push(articles[articleTurn % articles.length]);
    }

    // If the pool has fewer than three topics, fill remaining places with
    // other articles. A small pool may legitimately produce fewer than three.
    for (var index = 0; selected.length < 3 && index < candidates.length; index += 1)
    {
        var candidate = candidates[(day + index) % candidates.length];

        if (!selected.includes(candidate))
        {
            selected.push(candidate);
        }
    }

    var cards = document.createDocumentFragment();

    selected.forEach(function (card, index)
    {
        var copy = card.cloneNode(true);

        copy.querySelector('[data-feature-number]').textContent = String(index + 1).padStart(2, '0');
        cards.appendChild(copy);
    });

    // Build everything before replacing the static links. Unsupported browsers
    // or an unavailable script keep the rendered fallback instead.
    grid.replaceChildren(cards);
})();
