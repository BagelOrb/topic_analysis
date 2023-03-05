<a rel="license" href="http://creativecommons.org/licenses/by-nc/3.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/3.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/3.0/">Creative Commons Attribution-NonCommercial 3.0 Unported License</a>.

# Topic Analysis
Simple scripts for performing topic analysis on twitter data.
We explore several approaches and various variations on those approaches.
The most promising approaches are based on Dirichlet distributions, but they suffer from some inherent limitations.

This document discusses several techniques which can be used for NLP for topic analysis and concludes with some considerations on the dataset and possible directions for future work.

## Bigrams
Bigrams could be used to create better tokens in English. Instead of using single words as tokens we can use canonical phrases instead such as 'email address' and 'confirmation number'. This method also extract canonical phrases such as 'could you please' and 'happy to help'.

While amending the tokenization with these phrases could improve the readability, accuracy and comprehensibility of the resulting topics, the positive effects are expected to be rather small, since in general speech only a small part is bigrams. Moreover, it takes computation power and implementation effort. 

It might be worth revisiting this idea.

## Term Frequency - Inverse Document Frequency
The TF-IDF score can help in classifying documents, but it seems that it is not particularly well suited for tweets and better suited for longer documents such as articles. In longer articles it is more likely that terms will occur more than once and that these terms are highly significant for the topic of the document, whereas in tweets most often words only appear once. The TF-IDF score of tweets is also dominated by the length of the tweet, since the frequency of terms is their occurrence divided by the total length of the document. 

A topic analysis technique based on TF-IDF might be interesting for the analysis of longer documents, but for short documents such as tweets the score does not constitute a meaningful indicator.

## Specificity and stop words
When performing common topic analysis techniques on unprocessed data one will often find that needlessly much time is spent on meaningless words such as 'the' and 'to'. A common technique for dealing with this is filtering out those *stop words*.

However, this approach only shifts the problem to the slightly less meaningless words. According to Zipf's law the frequency of usage of a word is inversely proportional to its rank. I submit that the meaningfulness of a word is also inversely proportional to its usage. The less a word is used to more specific it is, and therefore the more significant it is for defining a topic.

One way of implementing this in our topic analysis methods is by weighing sample words or resulting topic words by their frequency $f$:

$$ w = \frac{1}{f} $$

We can also give a Bayesian interpretation to this score, since

$$ P(topic|word) = \frac{P(word|topic) P(topic)}{P(word)} $$

When evaluating a topic $P(topic)$ is constant, so the term drops out when comparing the different words for a topic.
We tried modeling $P(word)$ both from the frequency of words in the dataset as well as the frequency of words in a larger dataset, which incorporates other twitter data and the Brown corpus. See [Dataset considerations].

This specificity score neatly reduces the impact of stop words and gradually gives more weight to words less 'stoppy'.
However, it also gives extreme weights to unique words which only appear once in the dataset, such as 'heeeeeelp'.
In order to tackle this problem we tried several approaches:

- Assign a score of zero to words only occurring once in the dataset.
- Multiply the original score with the specificity score: $P(topic|word)  P(word|topic) \sim P(word|topic)^2 / P(word) $

These specificity scores were used in weighing the word samples in K-means clustering, and weighing the word scores for displaying the most significant words of a topic in LDA and HDP.

## K-means clustering
We can cluster the data into K clusters if we map the data to a metric space first; we can use word2vec to map words to vectors in that space.
One naive method is to do the clustering on a mapping on the individual words, rather than on the whole document.

While performing clustering on the individual words rather than the documents is severely limited, we can already see an inherent problem to this approach. How will we represent the topic? What does the center of a cluster really mean?

We could pick some words with a high specificity close to the cluster center, but that doesn't capture the extent of the cluster - it only captures the center.

Moreover, while word2vec should map words which are similar to nearby locations in the space, no guarantee is given as to whether more unrelated words are farther away from each other. The mapped space can be highly heterogeneous, with a high amount of topic changes over an intermediate distance. Furthermore, the word2vec mapping obscures the interpretability of our eventual topics, since the mapping does not have a straightforward interpretation.

## Latent Dirichlet Allocation
LDA models a document as an unstructured bag of words belonging to several categories. An LDA will be optimized such that the topic frequencies and their word frequencies accurately portray frequency of words in the documents. The result is a set of topics which consist of an assignment of a probability $P(word|topic)$ to each word in the dictionary. As such it doesn't consider the word order and therefore ignores all meaning that arises through grammar.

For LDA we choose a predetermined number of topics and display the 10 most relevant ones. For each topic we display, we display the most relevant words for that topic. 
Some words are highly probable in any topic, such as 'try' or 'reply', so looking at these probabilities without considering their specificity isn't very productive. That's why we order the words on a score based on their probability and their specificity instead and display only the most relevant ones.

However, often the most relevant/specific words of an LDA topic don't constitute what a layman would call a topic. The semantic coherence between the words is often obscure and it takes effort to see what links these words together - if there is a pattern at all.

With too many topics, multiple topics collapse to the same one. This is not overfitting, but a limitation of LDA's. Perhaps more training can help in this. However, once multiple topics have properly mode collapsed there's not much that the hill-climbing optimizer can do to untangle them.


## Hierarchical Dirichlet Process
An HDP is similar to an LDA, but the number of topics is determined by optimization, rather than being given by the user.
It therefore suffers from the same limitations as mentioned above.

## Dataset considerations
If a topic is prevalent throughout the dataset, we need another dataset to discover that fact. If most documents are about customer service than this fact might be interesting or not, depending on whether the dataset was specifically chosen from customer service data or not. The fact that most data is about customer service might be news to the company. It might therefore be interesting to compare the dataset to other data in order to find out which topics are prevalent in the datasat which aren't prevalent in other data.

How many topics would we expect? This depends on what the questioner means by 'topic'. We could divide the data into very general topics like ['discussion', 'complaint', 'inspirational'], or we could divide the data into more specialized topics such as ['games', 'faith', 'science', 'transport', etc.]. The number of topics we expect depends on how we mean to ask the question. We could therefore expect there to be a number of local optima when we try to optimize the number of topics in any topic analysis - each of which would be a valid strategy for answering the question.

What do we want to learn? Analyzing data without asking a specific question is like looking through a haystack not sure if you want to find a needle or a piece of hay. We should always be aware of the company for which we analyze data so that we can interpret what the results of our topic analysis means for that wider context.

## Future work
Performing a plain topic analysis on the basis of the word frequencies in the documents does not provide satisfactory results.

For example, when we employ topic analysis on a dataset of customer service data the most prevalent topics will revolve around concepts such as 'help', 'problem' and 'sorry'. However, those topics were to be expected, since the dataset is on customer service data. These topics aren't insightful to the company.

Furthermore, finding out what the subjects are with which people are having problems requires a syntactic and/or semantic understanding of a document beyond word occurrence frequency.

The syntactic information is crucially required to disambiguate "The wifi is working. I don't need help." from "The wifi isn't working. I need help." However, parsing the documents is beyond the scope of this project.

Besides those, some technical jargon might be required in order to determine what are the different synonyms of a word, which can depend on the field and subject matter of the dataset. With enough data such synonyms could be automatically extracted, but input from a field expert might be required to verify those synonyms.

Often a company wants to know what are the *current* talking points. In order to bias the results more toward recent topics we might weigh the documents by the inverse of their age, or leave out all documents older than some given data. Since in production we would need to continually update the model with newer information it might make sense to use a weighted moving average.

Some other interesting directions to analyze the twitter data is to process emoji, mentions and hashtags. Performing a sentiment analysis can help to determine which topics are more pressing than others.

Besides more involved techniques for performing topic analysis, we might also want to have more data. Tweets can be annotated using the user name, time and date,  Furthermore, in order to get a clear view of the company needs and type of data in the dataset it might be useful to have an in depth conversation with a representative.
