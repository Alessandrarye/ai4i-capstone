# The Whole Story: A Predictive Maintenance Platform for Small Machine Shops

*A narrative technical walkthrough of the capstone project, written to be understood, not just read.*

---

## 1. The problem, as a shop owner lives it

Picture a job shop with a dozen machines: a couple of lathes, some mills, maybe a grinder that predates the owner. Every machine that's running is making money. Every machine that isn't is losing it, and losing it fast, because small shops quote tight margins and promise delivery dates that assume everything works.

When a spindle bearing fails mid-run, the cost isn't just the part. It's the scrapped workpiece, the missed delivery, the emergency service call at premium rates, and the two days waiting for a technician who services the entire region. Industry figures put unplanned downtime in the hundreds of dollars per hour even for small operations, and the failures rarely announce themselves politely.

Here's the frustrating part: machines usually do announce themselves. Bearings run hotter before they seize. Torque climbs as tools dull. A good machinist with twenty years of experience feels these things. But that machinist is also running three other machines, training the new hire, and quoting next week's jobs. The signals are there; nobody has the attention to watch them all.

Large manufacturers solved this years ago with predictive maintenance platforms. Those platforms assume enterprise budgets, cloud subscriptions, dedicated reliability engineers, and a willingness to stream production data to someone else's servers. A twelve-machine shop in central Ohio has none of those, and often an active aversion to the last one.

**The product thesis in one sentence:** the sensing and the math behind predictive maintenance have become cheap enough to run on a $300 computer sitting inside the shop, so small manufacturers no longer need to choose between enterprise pricing and running to failure.

## 2. Why now: on-prem, cloud, and back to the edge

There's a historical arc that makes this moment specific rather than generic.

Computing for industry started on premises because there was no alternative: mainframes, then minicomputers, then PLCs and SCADA systems bolted to the shop floor. It was local because it had to be.

Then the cloud era inverted everything. From roughly 2010 onward, the assumption became that data flows up: sensors stream to a data center, models train and score remotely, dashboards render from someone else's infrastructure. This unlocked scale, but it hard-wired three costs into the product category: recurring subscription pricing, dependence on connectivity, and the requirement that your operational data leave your building. Enterprises absorbed all three. Small shops couldn't, and mostly didn't.

The third phase is the one we're in. Hardware got absurdly capable at the low end: a fanless mini PC now carries more compute than the servers that ran early cloud ML. Meanwhile the models that matter for tabular sensor data, gradient-boosted trees and isolation forests, are computationally modest. They don't need a GPU cluster; they barely need a GPU. The heavy machinery of the cloud era turns out to be unnecessary for this problem class.

So the edge isn't a compromise here. It's the correct architecture: inference happens feet from the machine producing the data, nothing leaves the building, there's no subscription meter running, and the shop owns the whole stack the way they own their machines. This resonates with how shop owners already think. They buy equipment; they distrust rent.

## 3. The data: what AI4I 2020 is and why it's an honest stand-in

Real shops don't hand students their sensor telemetry, so the project builds on the **AI4I 2020 Predictive Maintenance Dataset** from the UCI Machine Learning Repository (Matzka, 2020). It's a synthetic dataset, and that word needs to be owned rather than hidden: it was constructed by a researcher in industrial AI to reflect real predictive maintenance behavior that companies won't publish, because actual failure data is commercially sensitive.

The dataset contains **10,000 records**, each representing a machining cycle, with:

- **Air temperature (K)**: ambient conditions, varying around roughly 300 K
- **Process temperature (K)**: running about 10 K above air temperature
- **Rotational speed (rpm)**: spindle speed, inversely related to torque as real machines are
- **Torque (Nm)**: centered around 40 Nm
- **Tool wear (min)**: accumulated minutes on the current tool
- **Type (L/M/H)**: a product quality variant, low, medium, or high, which also shifts operating parameters

And the labels: a binary **Machine failure** flag, true for **339 of the 10,000 records, about 3.4 percent**, plus five columns recording *why* a failure happened.

## 4. The physics of failure: the five modes

This is the part of the dataset worth knowing cold, because it's where the ML connects to the machining, and it's exactly the territory a manufacturing-savvy questioner will probe.

**Tool wear failure (TWF).** Tools don't last forever. In the dataset, tools fail somewhere in the 200 to 240 minute wear window. In a real shop this is the most familiar failure: a dull tool chatters, then chips, then breaks.

**Heat dissipation failure (HDF).** This one is subtle and my favorite to explain. It occurs when the gap between process temperature and air temperature is small (under about 8.6 K) *while* rotational speed is low (under about 1380 rpm). Physically: a slow-turning machine that can't shed heat into its environment is cooking itself. Neither condition alone is dangerous; the combination is. This is why the model needs to see feature interactions, and it's the first argument for tree-based models over anything linear.

**Power failure (PWF).** Mechanical power is torque times angular velocity. The dataset encodes a safe operating band, roughly 3,500 to 9,000 watts; outside it, the process fails. Too little power and the cut stalls; too much and something gives. Again, no single sensor tells you this. You have to multiply two of them.

**Overstrain failure (OSF).** The product of tool wear and torque exceeding a threshold, and the threshold depends on the machine Type: lower-quality variants tolerate less. A worn tool under high load snaps. This mode is why Type belongs in the feature set.

**Random failure (RNF).** A small fraction of failures happen for no reason encoded in the sensors, because reality is like that. This mode is essentially unlearnable, and knowing it exists sets an honest ceiling on model performance: perfect recall is not on the table, and anyone claiming it should be suspected of leakage.

Two practical notes from this. First, one quirk to verify during EDA: the failure-mode columns and the overall Machine failure flag don't align perfectly in a handful of rows, a known wrinkle in this dataset, and catching it in exploration signals care. Second, and more importantly, the failure modes are *why* the engineered features exist, which brings us to the modeling.

## 5. Framing the ML problem

**The target** is the binary Machine failure flag. Predicting the specific failure mode is tempting and is deliberately deferred: with only 339 failures split across five modes, some modes have a few dozen examples, which is not enough to model responsibly. Multi-label failure-mode prediction goes on the roadmap; the capstone predicts fail or not-fail.

**The leakage trap.** The five failure-mode columns (TWF, HDF, PWF, OSF, RNF) *define* the target. Include any of them as features and the model achieves near-perfect scores while learning nothing, because it's reading the answer key. They are dropped from the feature matrix entirely and used only in analysis: a breakdown of failures by mode makes an excellent EDA visual and a great talking point, but they never touch the model. This is the single most common way to fail on this dataset, and being able to explain it crisply is worth more than any accuracy number.

Also dropped: the row ID and the Product ID. The product ID's letter prefix just repeats the Type column, and the number is an index. Indexes that correlate with the target are another classic leakage path.

**The features** are the five sensor readings plus Type (one-hot encoded), and then two engineered features that translate the failure physics into columns the model can see directly:

- **temp_delta** = process temperature minus air temperature. This hands the model the HDF mechanism.
- **power** = torque × rotational speed (converted to consistent units). This hands it the PWF mechanism.

Gradient-boosted trees can discover interactions on their own, but giving them the physically meaningful combinations directly makes the model both better and more explainable. It also produces the best line in the project: *the model watches the same physics a good machinist feels.* Feature importance plots that rank temp_delta and power highly aren't just validation of the model; they're validation that the model agrees with mechanical intuition.

## 6. The imbalance problem, or why accuracy is a lie here

With 3.4 percent positives, a model that predicts "never fails" for everything scores 96.6 percent accuracy while being completely useless. This single fact reorganizes the entire evaluation approach.

**Handling the imbalance:** the primary tool is class weighting, telling the learner that misclassifying a failure costs proportionally more than misclassifying a healthy cycle (scikit-learn's `class_weight='balanced'`, or `scale_pos_weight` in XGBoost). Synthetic oversampling (SMOTE) is run as a comparison in the notebook, but class weights are the default because they change the loss function rather than manufacturing artificial data points, and on tabular data of this size they typically perform as well or better with less machinery to defend.

**The metrics that matter:**

- **Recall on the failure class**: of the failures that occurred, what fraction did we catch? This is the metric a shop owner cares about, because a missed failure is the expensive event.
- **Precision on the failure class**: of our alarms, what fraction were real? This governs whether the owner keeps listening. A tool that cries wolf gets unplugged.
- **PR-AUC** (precision-recall area under curve) as the summary metric, because ROC-AUC flatters models on imbalanced data.

**The threshold is a business decision, not a math decision.** The model outputs a probability; someone has to choose where the alarm fires. Since a missed failure (scrapped parts, dead machine, emergency repair) costs far more than a false alarm (a technician checks a healthy machine), the threshold tunes toward recall. The target framing: *catch roughly nine of ten failures while keeping false alarms to a handful per thousand cycles.* Stating the trade-off in those terms, instead of quoting an F1 score, is what separates a product from a homework assignment.

**Calibration.** The dashboard displays failure probabilities, and a gauge reading 80 percent should mean that historically, readings like this failed about 80 percent of the time. Raw model scores don't automatically satisfy that, so the pipeline includes a calibration check (reliability curve) and, if needed, a calibration wrapper. This is a small step that most student projects skip, and it's precisely the kind of detail that survives hostile questioning.

## 7. The models, and why two of them

**Logistic regression goes first**, not because it will win, but because it's the honest baseline. It's fast, interpretable, and establishes the floor. If a fancier model can't beat it meaningfully, the fancier model isn't earning its complexity.

**Gradient boosting is the workhorse** (HistGradientBoostingClassifier or XGBoost). The failure physics is interaction-heavy: HDF is a temperature condition *and* a speed condition; OSF is wear *times* torque *conditioned on* Type. Linear models see each feature in isolation; boosted trees natively carve out these joint regions. The expected result, and the slide it produces, is a visible gap between the baseline and the boosted model that can be explained mechanistically rather than hand-waved: *the failures live in corners of the feature space that only interaction-aware models can reach.*

**Isolation Forest is the second system, not a competitor.** The classifier is supervised: it learns the failure patterns present in the training data, and it will be good at exactly those. But real machines invent new problems. The anomaly detector is unsupervised: it learns what *normal* looks like and flags anything sufficiently strange, regardless of whether that strangeness matches a known failure mode. The two cover each other's blind spots: the classifier catches the failures you've seen before, the anomaly detector raises a hand at the ones you haven't. On the dashboard they surface differently: the classifier drives the "failure risk" gauge, the anomaly score drives an "unusual behavior" flag. (Scope discipline note: this layer is the stretch goal. If the timeline compresses, it's the first thing cut, and the architecture loses nothing structural without it.)

## 8. The system: from CSV to something that feels alive

The ML is maybe a third of the project. The rest is the part that makes it a product, and it's where the full-stack training pays off.

**PostgreSQL** holds four tables: machines, readings, predictions, and alerts. Two design choices matter. Predictions live in their own table with a `model_version` column, so a retrained model can rescore historical readings and be compared against its predecessor; that column is the MLOps story beginning on day one. Alerts are also their own table, with severity and an acknowledged flag, so the dashboard has an event feed and an "acknowledge" button, the small touches that make an interface feel operational rather than academic.

**FastAPI** exposes a deliberately small surface: ingest a reading, list machines with current risk, machine detail with history, the alert feed, acknowledge an alert, and a health check. The load-bearing decision is that **ingestion triggers scoring inline**: when a reading arrives, the API stores it, runs the model, stores the prediction, and fires an alert if the probability crosses threshold, all in one request. One call drives the entire pipeline, which keeps the system deterministic and the demo bulletproof.

**React** renders the shop floor view: a card per machine with a risk gauge, sparklines of recent sensor history, and the alert feed. The design target is a glance: an owner walking past a wall-mounted screen should absorb the state of the shop in two seconds. Green, green, green, amber, and their eyes go exactly where they should.

**The replay script** is the piece that turns a static dataset into a living demo. AI4I is a CSV; a demo of a CSV is a table. The replay script feeds rows through the ingestion endpoint every few seconds, as if machines were reporting live. Risk scores drift, a gauge climbs from green through amber to red, an alert fires. For the presentation, the replay is scripted around one machine whose readings degrade convincingly: *watch Machine 7, its tool wear has been climbing all week.* A narrative demo rehearsed around the same two minutes beats improvised clicking every single time.

**Deployment** is Docker Compose: postgres, API, and frontend as three containers. Development happens on the Ubuntu desktop; the destination is a dedicated fanless mini PC, which is not a convenience but the thesis made physical. The demo unit *is* the product: this box, magnet-mounted to the side of a machine cabinet, is the entire infrastructure requirement.

## 9. What this semester proves, and what comes after

The capstone proves the core loop: sensor readings in, calibrated risk out, on hardware a shop can afford, with no data leaving the building. The roadmap shows the loop was designed to grow:

**Phase 2, real ingestion.** Swap the replay script for MQTT, the messaging protocol industrial sensors actually speak. The API doesn't change; only the source does. Ideally this phase names a real design partner, a local shop recruited through instructor introductions, running one instrumented machine.

**Phase 3, remaining useful life.** Graduating from *will it fail?* to *how many hours until it does?* This is regression on time-series data (the territory of datasets like NASA's CMAPSS), and it changes the owner's decision from "check this machine" to "schedule the bearing swap for Friday."

**Phase 4, drift and retraining.** Shop conditions change: seasons, tooling, operators. A deployed model quietly goes stale. Monitoring input distributions for drift and retraining on accumulated local data is what turns a demo into a dependable tool, and the `model_version` column has been waiting for it since the first table was created.

**Phase 5, learning across shops without sharing data.** Transfer learning to bootstrap new machines from existing models, and eventually federated learning, where multiple shops improve a shared model while raw data never leaves any building. This is the roadmap item that rhymes perfectly with the privacy pitch, and richer sensors (vibration, acoustics) open the door to deep learning on spectrograms when the problem finally demands it.

The arc, compressed: rigorous classical ML now, time-series and MLOps next, multi-shop learning at the horizon. The project doesn't end when the class does.

---

## Appendix: The hard questions, answered in advance

**"It's synthetic data. Isn't this all fake?"**
The data is synthetic; the failure physics it encodes is not. It was built by an industrial AI researcher specifically because real failure telemetry is commercially guarded. The capstone's claim is carefully scoped: it proves the *platform*, the full loop from ingestion to calibrated alert on edge hardware. Validating against real telemetry is explicitly phase 2, with a design partner, and the architecture was built so that swapping the data source touches nothing downstream. Owning this limitation preempts it.

**"Your accuracy is 97 percent? Impressive."**
Trap question, possibly unintentional. The answer: accuracy is nearly meaningless at 3.4 percent positives, since predicting "never fails" scores 96.6 percent. The metrics that matter are recall and precision on the failure class and PR-AUC, with the threshold chosen from the cost asymmetry between missed failures and false alarms.

**"Why not deep learning?"**
Because the data is tabular and modest in size, and on tabular data gradient-boosted trees remain the consistently strong choice while training in seconds on CPU, which is itself part of the edge thesis. Deep learning enters the roadmap exactly when the data type demands it: vibration and acoustic signals as spectrograms, in a later phase. Using the biggest model available is not rigor; matching the model to the problem is.

**"Why not the cloud? Everything is cloud."**
Three reasons, in the owner's language: recurring cost (subscriptions scale with machines; a mini PC is bought once), connectivity (shops have concrete walls and metal everywhere, and a maintenance tool that dies with the internet is a liability), and data custody (production telemetry reveals volumes, schedules, and clients, and small manufacturers are rightly wary of streaming it out). None of this is cloud hostility; it's fitting the architecture to the customer.

**"How is this different from what machine OEMs ship?"**
OEM monitoring is per-machine, per-brand, and often per-subscription. A real shop floor is a mixed fleet spanning decades and manufacturers. This platform is the brand-agnostic layer above that mix, one view of the whole floor, owned by the shop.

**"What if the model just alarms constantly? Nobody trusts a car alarm."**
That's the precision side of the threshold trade-off, and it's treated as a first-class product concern: the threshold tunes for high recall *subject to* a false-alarm budget stated in operational terms (a handful per thousand cycles), probabilities are calibrated so the gauge means what it says, and alerts require acknowledgment so the system knows what was seen. Alert fatigue is a design problem, and it's designed for.

**"What about the failures the model has never seen?"**
Two answers. The random failure mode in the data sets an honest ceiling: some failures carry no sensor signature, and no model catches them. For novel-but-detectable problems, that's the Isolation Forest's job: it models normalcy rather than known failures, so it flags strange behavior the classifier has no category for. Known failure patterns and unknown strangeness are covered by two different systems on purpose.

**"Could you have just written threshold rules instead of ML?"**
For any single failure mode, nearly. The value shows up in the interactions and the probabilities: HDF and OSF live in joint regions of multiple variables, thresholds per machine type multiply the rule count, and rules give binary answers while the model gives calibrated risk that supports *scheduling* rather than panicking. Rules are also frozen; the model retrains as local data accumulates. That said, a rules-vs-model comparison makes a strong notebook section, and conceding what rules do well buys credibility for the claim of what they don't.

---

## Reference

Matzka, S. (2020). *AI4I 2020 Predictive Maintenance Dataset* [Data set]. UCI Machine Learning Repository. https://doi.org/10.24432/C5HS5C
