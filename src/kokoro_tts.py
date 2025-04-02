from kokoro import KPipeline
import soundfile as sf
import os
import uuid

class KokoroTTSGenerator:
    def __init__(self, lang_code='es', voice='af_heart', output_dir='src/output/kokoro'):
        self.pipeline = KPipeline(lang_code=lang_code, repo_id='hexgrad/Kokoro-82M')
        self.voice = voice
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        

    def generate_audio(self, text):
        generator = self.pipeline(text, voice=self.voice, speed=0.8)
        
        for i, (gs, ps, audio) in enumerate(generator):
            # Generate a unique filename using UUID
            output_filename = f'{self.output_dir}/{uuid.uuid4()}.wav'
            
            # Save the audio to a WAV file
            sf.write(output_filename, audio, 24000)
            
            # Yield the filename (or audio data) for further use (e.g., WebSocket response)
            yield output_filename  # Or yield audio if you'd like to send audio data

def main():
    text = '''
   Of my earliest childhood I can form no consecutive picture; I shall therefore pass over it quickly. Certain incidents stand out with extraordinary vividness, but the chain uniting them is wanting, and it is even impossible for me to be quite sure as to the order in which they occurred. Some are so trivial that I do not know why I should remember them; others, at the time, doubtless, more important, have now lost their significance; and countless others, again, I must have completely forgotten. But it occurs to me, on looking back deliberately, that I have changed very little from what I was in those first years. I have developed, but what I was then I am now, what I cared for then I care for now. In other words, like everybody else, I came into this world a mere bundle of inherited instincts, for the activity of which I was no more responsible than for the falling of last night’s rain.

Of the dawning of consciousness I have no recollection whatever. Back farther than anything else there reach two impressions—one, of being set to dance naked on a table, amid the laughter of women, and the rhythmic clapping of their hands; the other, probably later in date, of what must have been a house-cleaning, stamped on my mind by an inexplicable fear of those flakey collections of dust which gather under furniture that has not been moved for a long time. By then I had certainly learned to talk,[12] for those flakes of dust I called “quacks.” I do not know where the name came from, nor why I should have disliked “quacks,” but they affected me with a strange dread, and here was a whole army of them where I had never seen but one or two. Some stupid person running after me with a broom pretended to sweep them over me, and I started bawling at the top of my voice. Then, for consolation, I was lifted up to bury my nose in a bowl of violets, and the colour and sweetness of the flowers took away my trouble. Probably it was later than this that I first became aware of a peculiar sensibility to dress—not to underclothing, but to my outer garments. To be dressed in a new suit of clothes gave me a curious physical pleasure—a feeling purely sensual, and that must, I imagine, have been connected with the dawn of obscure sex instincts. Such things can be of little interest save to the student of psychology, and it would be tedious to catalogue them in full, but I have no doubt myself that if they, and others, had been intelligently observed, the whole of my future could have been cast from them. To me, I confess, they throw a disquieting light upon all human affairs, reviving that sombre figure of destiny which overshadowed the antique world.

Another and happier instinct which I brought with me from the unknown was an intense sympathy with animals. There was not a cat or dog or goat or donkey in the village that I had not struck up a friendship with. I even carried this sympathy so far as to insist on feeding daily the ridiculous stone lions which flanked the doorsteps at Derryaghy House. I don’t think I ever actually believed that their morning meal of stale bread gave much pleasure to these patient beasts, and I had with my own eyes seen sparrows and thrushes—who very soon came to look out for me—snatch it from them before my back was turned; still, I persevered, stroking their smooth backs, kissing their cold muzzles, just as I lavished depths of affection on a stuffed,[13] dilapidated, velvet elephant who for many years was my nightly bed-fellow.

My only impressions of my mother go back to those days or, possibly, earlier—a voice singing gay songs to the piano, while I dropped asleep in my bed upstairs—and then, again, somebody lifting me out of this bed to kiss me, the close contact of a face wet with tears, the pressure of arms that held me clasped tightly, that even hurt a little. That is all. I cannot remember how she looked, or anything else. On the evening when she said good-bye to me and left our house, I knew she was crying, but, though it called up in me a sort of solemn wonder, I did not understand it, and went to sleep almost as soon as she put me back into my bed. It was not till next day that my own tears came, with the first real sorrow I had known.

There follows now a sort of blank in my recollections, which continues on to my ninth or tenth year. I do not know why this period should have been so unproductive of lasting impressions. It is like a tranquil water over which I bend in the hope of seeing some face or vision ripple to the surface, but my hope is disappointed. Nothing emerges—not even a memory of any of those ailments, measles and what not, from which, in common with other children, I suppose I must have suffered. Nor can I recollect learning to read. I can remember quite well when I couldn’t read, for I have a very distinct recollection of lying on my stomach, on the parlour floor, a book open in front of me, along whose printed, meaningless lines I drew my finger, turning page after page till the last was reached, though what solemn pleasure I could have got from so dull a game—surely the most tedious ever invented—I now utterly fail to comprehend.

I was always very fond of being read to, except when the story had a moral, or was about pious children, when[14] I hated it. The last of these moral tales I listened to was called “Cassy.” I particularly disliked it, but I can remember now only one scene, where Cassy comes into an empty house at night, and discovers a corpse there. This had an effect on my mind which for several days made me extremely reluctant to go upstairs by myself after dark. “Jessica’s First Prayer,” “Vinegar Hill,” “The Golden Ladder”—how I loathed them all! Every Sunday, after dinner, my father would take some such volume from the shelf, open it, and put on his spectacles. Holding the book at a long distance from his eyes, he would read aloud in a monotonous, unanimated voice, while I sat on a high-backed chair and listened, for I was not allowed to play the most innocent game, nor even to go out for a walk. These miserable tales were full of the conversions of priggish children; of harrowing scenes in public-houses or squalid city dens. Some of them were written to illustrate the Ten Commandments; others to illustrate the petitions in the Lord’s Prayer. They contained not the faintest glimmer of imagination or life: from cover to cover they were ugly, dull, unintelligent, full of death, poverty and calamity. On the afternoon when “Cassy’s” successor was produced—I forget its name—in a state of exasperation, brought about by mingled boredom and depression, I snatched the book out of my father’s hands and flung it on the fire. I was whipped and sent to bed, but anything was better than “Vinegar Hill,” and next Sunday, also, I refused to listen. Again, with tingling buttocks, I was banished to the upper regions, but really I had triumphed, for when the fateful day came round once more, the book-case was not opened, and I had never again to listen to one of those sanctimonious tales.

Fairy stories and animal stories were what I liked best, while some of the old nursery rhymes and jingles had a fascination for me.

[15]

“How many miles to Babylon?
Three score and ten.
Can I get there by candlelight?—
Yes, and back again.”
Was it some magical suggestion in the word “candlelight” that invariably evoked in a small child’s mind a definite picture of an old fantastic town of towers and turrets, lit by waving candles, and with windows all ablaze in dark old houses? Many of these rhymes had this quality of picture making:

“Hey, diddle diddle,
The cat and the fiddle,
The cow jumped over the moon:
The little dog laughed
To see such sport
When the dish ran away with the spoon.”
That, I suppose, is pure nonsense, yet the magic was there. Before and after the cow made her amazing leap the stuff was a mere jingle: it was the word “Moon” that brought up the picture: and I saw the white, docile beast, suddenly transformed, pricked by the sting of midsummer madness, with lowered head and curling horns, poised for flight, for the wonderful upward leap, while a monstrous, glowing moon hung like a great scarlet Chinese lantern in the clouds, low against a black night.

At this time I had few books I cared for, but as I grew older, and my powers of understanding increased, I found more, for up at Derryaghy House was a whole library in which I might rummage without any other interference than that my father could exercise from a distance. Sometimes when I brought a book home which he did not approve of, he would send me back with it; but if I had begun it I always finished it. I had made this a rule; though, on the other hand, if I had not begun it, I let my father have his way.

Everything connected with the East had a deep attraction[16] for me—or, shall I say, what I imagined the East to be—a country of magicians and mysterious talismans, of crouching Sphinxes and wonderful gardens. I delighted in the more marvellous stories in the “Arabian Nights,” and I regretted infinitely that life was really not like that. To go for a walk and fall straightway on some wonderful adventure, that was what I should have loved. I remember poring over a big folio of photographs of Eastern monuments. Those mystical, winged beasts with human heads, in their attitude of eternal waiting and listening, touched some chord in my imagination: they had that strangeness which I adored, and at the same time they had an odd familiarity. I appeared to remember—but, oh, so dimly!—having seen them before, not in pictures, but under a hot, heavy, languid sun, long, long ago. The luxuriousness, the softness and sleepy charm of the Asiatic temper—I had something in common with it, I could understand it. The melodious singing of a voice through the cool twilight; the notes of a lute dying slowly into silence; another voice, low and clear and musical, reading from the “Koran”—where had I heard all that? I pictured great coloured bazaars, where grave merchants with long white beards sat cross-legged and silent, where beautiful, naked, golden-skinned slaves stood waiting for a purchaser, where you could buy silken carpets that would carry you over the world, and black, ebony horses, swifter than light.

    '''
    
    tts_generator = KokoroTTSGenerator(lang_code='a', voice='af_heart')
    
    # Generate and save audio, yielding each file
    for file in tts_generator.generate_audio(text):
        # You can yield or send this to your WebSocket connection here
        print(f'Generated and saved: {file}')

if __name__ == "__main__":
    main()
