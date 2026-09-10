# RAG (Retrieval-Augmented Generation) — সম্পূর্ণ নোট

## ১. RAG আসলে কী, আর কেন দরকার?

LLM (যেমন GPT, Claude) একটা নির্দিষ্ট সময় পর্যন্ত ডেটা দিয়ে train করা থাকে। এর সমস্যা:
- নতুন/private/আপডেটেড তথ্য জানে না (যেমন তোমার কোম্পানির internal ডকুমেন্ট)
- Hallucinate করতে পারে (ভুল তথ্য confidently বলে)
- পুরো একটা বড় ডকুমেন্ট prompt-এ পাঠানো ব্যয়বহুল ও context limit-এ আটকে যায়

**RAG-এর সমাধান:** LLM-কে answer দেওয়ার আগে relevant তথ্য "retrieve" করে দেওয়া হয়, যাতে LLM সেই context দেখে answer generate করে — নিজের memory থেকে guess না করে।

```
User Question → Retrieval (relevant info খোঁজা) → LLM (context + question দিয়ে answer)
```

এটাকে বলে **Retrieval-Augmented Generation** — Generation-কে Retrieval দিয়ে "augment"/শক্তিশালী করা হচ্ছে।

---

## ২. Embedding কী?

**Embedding** হলো টেক্সটকে সংখ্যার একটা array (vector)-এ রূপান্তর করা, যেখানে অর্থগতভাবে (semantically) কাছাকাছি টেক্সটের vector-ও কাছাকাছি থাকে।

উদাহরণ:
- "রাজা" এবং "রানী" এর embedding vector কাছাকাছি হবে
- "রাজা" এবং "কলা" এর vector অনেক দূরে হবে

প্রতিটা embedding model একটা fixed-size vector দেয়:
- `all-MiniLM-L6-v2` → 384 dimension
- OpenAI `text-embedding-3-small` → 1536 dimension

**কেন দরকার:** কম্পিউটার টেক্সটের "অর্থ" বোঝে না, কিন্তু সংখ্যার মধ্যে distance/similarity হিসাব করতে পারে। Embedding-ই সেই সেতু।

**Model বাছাইয়ের বিবেচনা:**
| | Local (sentence-transformers) | API (OpenAI) |
|---|---|---|
| Cost | ফ্রি | প্রতি request-এ চার্জ |
| Speed | Local hardware নির্ভর | Network latency আছে |
| Quality | ভালো, তবে OpenAI-এর বড় model থেকে একটু কম | সাধারণত বেশি ভালো |
| Privacy | ডেটা বাইরে যায় না | ডেটা API-তে যায় |

---

## ৩. Chunking কী?

একটা পুরো PDF/document একসাথে embed করলে সমস্যা হয়:
- Embedding model-এর input length limit থাকে
- বড় টেক্সটের embedding "average" হয়ে যায়, specific তথ্য হারিয়ে যায়
- Retrieval-এ পুরো ডকুমেন্ট ফেরত এলে LLM-এর context window নষ্ট হয়

তাই ডকুমেন্টকে ছোট ছোট **chunk**-এ ভাগ করা হয়, প্রতিটা chunk আলাদাভাবে embed করা হয়।

### Chunking Strategies:

**a) Fixed-size chunking**
নির্দিষ্ট সংখ্যক word/token নিয়ে chunk বানানো।
```
chunk_size = 500 words, overlap = 50 words
```
- সহজ, দ্রুত implement করা যায়
- সমস্যা: মাঝপথে একটা বাক্য/paragraph কেটে যেতে পারে

**b) Overlap কেন দরকার?**
Chunk-এর শেষে যদি গুরুত্বপূর্ণ তথ্য কাটা পড়ে, পরের chunk-এর শুরুতে সেটার কিছুটা repeat থাকলে context হারায় না।
```
Chunk 1: [word 0............word 500]
Chunk 2:              [word 450............word 950]
                       ↑ overlap zone (450-500)
```

**c) Recursive/semantic chunking**
প্রথমে paragraph/sentence বাউন্ডারি অনুযায়ী ভাগ করার চেষ্টা করে, তারপর দরকার হলে size অনুযায়ী আরও ভাগ করে। এতে অর্থ কম ভাঙে।

**d) Page-aware chunking** (আমাদের প্রজেক্টে যেমন করা হয়েছে)
প্রতিটা chunk-এর সাথে page number metadata হিসেবে রাখা, যাতে answer-এর সাথে "কোন পাতা থেকে এলো" সেটা citation হিসেবে দেখানো যায়।

**Trade-off:**
- ছোট chunk → বেশি precise retrieval, কিন্তু context কম
- বড় chunk → বেশি context, কিন্তু irrelevant তথ্যও চলে আসতে পারে (noise বাড়ে)

---

## ৪. Vector Search / Similarity Search

Vector search হলো: হাজার হাজার stored vector-এর মধ্যে থেকে query vector-এর সবচেয়ে কাছের (most similar) vector-গুলো খুঁজে বের করা।

### Similarity/Distance মাপার পদ্ধতি:

**Cosine Similarity** (সবচেয়ে বেশি ব্যবহৃত টেক্সট embedding-এর জন্য)
- দুটো vector-এর মধ্যে angle মাপে, magnitude নয়
- মান থাকে -1 থেকে 1, বেশি হলে বেশি similar
```sql
1 - (embedding <=> query_embedding) AS similarity   -- pgvector syntax
```

**Euclidean/L2 Distance**
- সরাসরি দুটো point-এর মধ্যে "straight-line" দূরত্ব
- মান যত কম, তত similar

**Dot Product**
- দ্রুততম হিসাব, কিন্তু vector normalized না হলে ভুল ফল দিতে পারে

### কেন "search" আলাদা RDBMS query থেকে?
Traditional SQL `WHERE` clause exact match বা range খোঁজে। Vector search "approximate nearest neighbor" (ANN) খোঁজে — লক্ষ লক্ষ vector-এর মধ্যে দ্রুত সবচেয়ে কাছেরগুলো বের করার জন্য বিশেষ index লাগে (যেমন IVFFlat, HNSW), কারণ প্রতিটার সাথে brute-force compare করলে ধীর হয়ে যাবে।

---

## ৫. Metadata Filtering

শুধু vector similarity যথেষ্ট না — অনেক সময় নির্দিষ্ট শর্ত অনুযায়ীও ফিল্টার করা দরকার:
- "শুধু এই ডকুমেন্টে সার্চ করো" (`document_name = 'file.pdf'`)
- "শুধু গত ৩০ দিনের মধ্যে upload হওয়া ডকুমেন্টে"
- "শুধু নির্দিষ্ট user-এর ডকুমেন্টে" (multi-tenant system-এ জরুরি)

Vector similarity + traditional SQL filter — দুটো একসাথে combine করা হয়:
```sql
SELECT * FROM document_chunks
WHERE document_name = 'file.pdf'   -- metadata filter
ORDER BY embedding <=> query_vector  -- vector similarity
LIMIT 5;
```

এতে দুটো লাভ: relevance (vector similarity) + precision (নির্দিষ্ট scope-এ সীমাবদ্ধ রাখা)।

---

## ৬. pgvector

PostgreSQL-এর একটা extension যা vector data type ও similarity search সমর্থন করে।

**সুবিধা:**
- তুমি যদি already PostgreSQL ব্যবহার করো, আলাদা কোনো নতুন ডাটাবেস দরকার নেই
- SQL-এর সব ক্ষমতা (JOIN, WHERE, transaction) vector search-এর সাথে একসাথে ব্যবহার করা যায়
- Metadata filtering স্বাভাবিকভাবেই সহজ (normal SQL columns)

**সীমাবদ্ধতা:**
- খুব বড় scale (কোটি কোটি vector)-এ dedicated vector DB-এর চেয়ে ধীর হতে পারে
- Index tuning (IVFFlat/HNSW) নিজে বুঝে সেট করতে হয়

---

## ৭. Qdrant

একটা dedicated, open-source vector database — শুধু vector search-এর জন্যই বানানো।

**সুবিধা:**
- বড় scale-এ অপ্টিমাইজড, দ্রুত
- Built-in advanced filtering, payload (metadata) সহজে handle করে
- HNSW index দিয়ে দ্রুত approximate search
- REST/gRPC API আছে, client library সহজ

**কখন pgvector বনাম Qdrant:**
| পরিস্থিতি | Choice |
|---|---|
| ছোট-মাঝারি project, already Postgres ব্যবহার করছো | pgvector |
| Millions+ vectors, high-performance দরকার | Qdrant |
| Learning purpose — দুটোই শেখা উচিত | দুটোই try করা ভালো |

---

## ৮. পুরো Pipeline একসাথে

```
PDF আপলোড
   ↓
Text Extraction (pypdf)
   ↓
Chunking (page-aware, overlap সহ)
   ↓
Embedding (প্রতিটা chunk → vector)
   ↓
Vector DB-তে Store (pgvector/Qdrant, metadata সহ)

── User একটা প্রশ্ন করে ──
   ↓
প্রশ্নটাও Embed হয়
   ↓
Vector Search (+ optional metadata filter)
   ↓
Top-K সবচেয়ে relevant chunks পাওয়া যায়
   ↓
LLM-কে prompt: "এই context দেখে উত্তর দাও"
   ↓
Answer + Source citation
```

## ৯. মনে রাখার মতো Key Points

- Embedding মানে "অর্থ"-কে সংখ্যায় রূপান্তর — কাছাকাছি অর্থ = কাছাকাছি vector
- Chunking-এর সাইজ ও overlap সরাসরি retrieval quality-তে প্রভাব ফেলে
- Cosine similarity টেক্সট embedding-এর জন্য সবচেয়ে common choice
- Metadata filtering ছাড়া large-scale RAG system practically ব্যবহারযোগ্য না
- pgvector সহজ শুরু করার জন্য ভালো, Qdrant বড় scale-এর জন্য
- RAG শুধু "search" না — শেষ ধাপে LLM যেভাবে prompt পায়, সেটার উপরেও answer quality অনেকখানি নির্ভর করে

---

## ১০. Interview-এ RAG কীভাবে Explain করবে

### a) ৩০ সেকেন্ডের "Elevator Pitch" (সাধারণ প্রশ্ন: "RAG কী, বলো তো")

এভাবে সহজ ভাষায় শুরু করো, তারপর দরকার হলে depth-এ যাও:

> "RAG মানে হলো LLM-কে answer দেওয়ার আগে relevant তথ্য খুঁজে দেওয়া, যাতে সে নিজের training data থেকে guess না করে, বরং দেওয়া context থেকে answer বানায়। এটা মূলত দুইটা ধাপ — প্রথমে retrieval (ডকুমেন্ট থেকে relevant অংশ খোঁজা vector similarity দিয়ে), তারপর generation (সেই context + question দিয়ে LLM answer বানায়)। এটা ব্যবহার করা হয় কারণ LLM-এর knowledge fixed একটা সময় পর্যন্ত, আর private/updated data সে জানে না — RAG দিয়ে সেই gap পূরণ করা যায়, hallucination কমে।"

### b) যদি জিজ্ঞেস করে: "তোমার প্রজেক্টে কীভাবে করেছো?" (STAR-এর মতো structure রাখো)

1. **Problem** — "আমি একটা Document Q&A API বানিয়েছি যেখানে user PDF আপলোড করে প্রশ্ন করতে পারে"
2. **Pipeline সংক্ষেপে বলো** — PDF → extract → chunk → embed → vector DB store → query time-এ similarity search → LLM answer
3. **Decision-গুলো explain করো, শুধু "কী করেছি" না, "কেন করেছি"**:
   - "আমি local `sentence-transformers` embedding ব্যবহার করেছি কারণ API cost এড়ানো যায়"
   - "Chunk-এ overlap রেখেছি যাতে বাক্যের মাঝে কেটে গেলে context না হারায়"
   - "pgvector বেছেছি কারণ Postgres already চিনি, আর metadata filtering সহজ হয় সাধারণ SQL দিয়ে"
4. **Trade-off নিয়ে বলতে পারলে extra points**: "Qdrant বড় scale-এর জন্য ভালো হতো, কিন্তু এই সাইজের প্রজেক্টে pgvector যথেষ্ট"

### c) সাধারণ Follow-up প্রশ্ন ও কীভাবে উত্তর দেবে

**Q: "Chunk size কেন এই সাইজ বেছেছো?"**
> "খুব ছোট chunk করলে context হারায়, খুব বড় করলে irrelevant তথ্য চলে আসে আর embedding-এর quality কমে। আমি 500 word এর মতো একটা balance রেখেছি, সাথে overlap যাতে boundary-তে তথ্য না কাটে।"

**Q: "Cosine similarity কেন, Euclidean distance না কেন?"**
> "টেক্সট embedding-এর ক্ষেত্রে vector-এর direction (অর্থ) গুরুত্বপূর্ণ, magnitude না। Cosine similarity শুধু angle মাপে, তাই এটা টেক্সট embedding-এর জন্য standard choice।"

**Q: "যদি হাজার হাজার ডকুমেন্ট হয়, system slow হয়ে যাবে না?"**
> "এই জন্যই ANN (Approximate Nearest Neighbor) index ব্যবহার করা হয়, যেমন IVFFlat বা HNSW — এগুলো প্রতিটা vector-এর সাথে brute-force compare না করে দ্রুত approximate ফলাফল দেয়। বড় scale-এ Qdrant-এর মতো dedicated vector DB বেশি optimized।"

**Q: "RAG আর fine-tuning-এর মধ্যে পার্থক্য কী?"**
> "Fine-tuning মডেলের weight-ই বদলে দেয় — নতুন knowledge model-এর ভেতরে "বেক" হয়ে যায়, কিন্তু ব্যয়বহুল ও update করা কঠিন। RAG model-কে বদলায় না, বরং প্রতিবার query time-এ বাইরে থেকে relevant তথ্য দেয় — তাই data update করা সহজ (শুধু নতুন ডকুমেন্ট database-এ যোগ করলেই হয়), আর cost অনেক কম।"

**Q: "Hallucination কীভাবে কমাও?"**
> "Prompt-এ স্পষ্টভাবে বলে দিই যে শুধু দেওয়া context থেকেই answer দিতে হবে, context-এ না থাকলে 'জানি না' বলতে হবে। সাথে source citation (কোন document/page থেকে answer এসেছে) দেখালে user নিজেও verify করতে পারে।"

### d) Tip: যা এড়িয়ে চলবে

- শুধু buzzword বলে যাওয়া ("pgvector, embedding, chunking" — নাম বললেই হবে না, *কেন* সেই choice সেটা বলতে পারা জরুরি)
- মুখস্থ definition আওড়ানো — বরং নিজের প্রজেক্টের উদাহরণ দিয়ে explain করলে বেশি convincing হয়
- Trade-off স্বীকার না করা — "pgvector best" না বলে "এই scale-এর জন্য pgvector যথেষ্ট, বড় হলে Qdrant বিবেচনা করতাম" — এভাবে বললে বোঝা যায় তুমি সত্যিই বুঝে করেছো, শুধু copy-paste করোনি
